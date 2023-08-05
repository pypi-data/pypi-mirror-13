import unittest
import time

from batchcompute import Client, ClientError
from batchcompute.resources import (
    JobDescription, DAG, TaskDescription, Parameters, Command,
    InputMappingConfig, GroupDescription, ClusterDescription,
)
from batchcompute.utils import get_logger, set_log_level

import config as cfg

logger = get_logger('batchcompute.tests.client', file_name="batchcompute_python_sdk.log")
set_log_level("DEBUG")

class TestClient(unittest.TestCase):

    def get_cluster_desc(self, image_id):
        cluster_desc = ClusterDescription()
        group_desc = GroupDescription()
    
        group_desc.DesiredVMCount = 1
        group_desc.InstanceType = 'ecs.t1.small'
        # group_desc.InstanceType = "ecs.t1.small" 
        cluster_desc.add_group('group1', group_desc)
        cluster_desc.Name = self.cluster_desc 
        cluster_desc.ImageId = image_id 

        logger.info("Cluster Desc: %s", cluster_desc)

        return cluster_desc

    def get_job_desc(self, cluster_id):
        job_desc = JobDescription()
        map_task = TaskDescription()
    
        # Create map task.
        map_task.Parameters.Command.CommandLine = "ping -n 3 127.0.0.1" 
        map_task.Parameters.Command.PackagePath = "" 
        map_task.Parameters.StdoutRedirectPath = cfg.LOG_PATH
        map_task.Parameters.StderrRedirectPath = cfg.LOG_PATH 
        map_task.InstanceCount = 3 
        map_task.ClusterId = cluster_id 

        logger.info("Map Task: %s", map_task)
    
        # Create task dag.
        task_dag = DAG()
        task_dag.add_task(task_name='Map', task=map_task)
    
        # find prime job description.
        job_desc.DAG = task_dag
        job_desc.Priority = 99 
        job_desc.Name = self.job_desc 
        job_desc.JobFailOnInstanceFail = True

        logger.info("Job Desc: %s", job_desc)
        
        return job_desc

    def setUp(self):
        self.cluster_desc = 'BatchcomputePythonSDKCluster' 
        self.job_desc = 'BatchcomputePythonSDKJob' 

        self.client = Client(cfg.REGION, cfg.ID, cfg.KEY, security_conn=True)

        self.clean_env()

    def tearDown(self):
        self.clean_env()

    def clean_env(self):
        cluster_filters = {
            'Name': self.cluster_desc,
            'State': 'Active'
        }
        for cluster in self.client.easy_list('clusters', **cluster_filters):
            print 'Delete cluster: ', cluster 
            self.client.delete_cluster(cluster.Id)

        job_filters = {
            'Name': self.job_desc,
            'State': ['Running', 'Waiting', 'Stopped']
        }
        for job in self.client.easy_list('jobs', **job_filters):
            print 'Stop job: ', job
            if job.State != 'Stopped':
                self.client.stop_job(job.Id)
            self.client.delete_job(job.Id)

    def get_new_cluster(self):
        cluster_desc = self.get_cluster_desc(cfg.WINDOWS_IMAGE_ID)
        res = self.client.create_cluster(cluster_desc)
        logger.info(res)
        return res.Id

    def testCreateCluster(self):
        self.get_new_cluster()

    def testChangeClusterDesiredVMCount(self):
        cluster_id = self.get_new_cluster()

        cluster_status = self.client.get_cluster(cluster_id)
        self.assertEqual(cluster_status.Groups['group1']['DesiredVMCount'], 1)

        desired_vm_count = 2
        self.client.change_cluster_desired_vm_count(cluster_id, group1=desired_vm_count)

        cluster_status = self.client.get_cluster(cluster_id)
        self.assertEqual(cluster_status.Groups['group1']['DesiredVMCount'], 2)

    def testDeleteCluster(self):
        cluster_id = self.get_new_cluster()
        self.client.delete_cluster(cluster_id)

    def testListCluster(self):
        cluster_ids = []
        for i in range(4):
            cluster_id = self.get_new_cluster()
            cluster_ids.append(cluster_id)
            time.sleep(4)

        for cluster_id in cluster_ids:
            self.assertTrue(cluster_id in self.client.easy_list('clusters'))

    def get_new_job(self):
        cluster_id = self.get_new_cluster()
        job_desc = self.get_job_desc(cluster_id)
        job_id = self.client.create_job(job_desc).Id
        self.assertEqual(self.client.get_job(job_id).State, 'Waiting')
        return job_id

    def get_stopped_job(self):
        job_id = self.get_new_job()
        self.client.stop_job(job_id)
        self.assertEqual(self.client.get_job(job_id).State, 'Stopped')
        return job_id

    def testCreateJob(self):
        job_id = self.get_new_job()

    def testStopJob(self):
        job_id = self.get_stopped_job()
        self.client.delete_job(job_id)

    def testDeleteJob(self):
        waiting_job_id = self.get_new_job()
        self.assertRaises(ClientError, self.client.delete_job, waiting_job_id)

        stopped_job_id = self.get_stopped_job()
        self.client.delete_job(stopped_job_id)
        self.assertTrue(stopped_job_id not in self.client.easy_list('jobs'))

    def testFinishJob(self):
        job_id = self.get_new_job()
        self.client.poll(job_id)

    def testListJob(self):
        job_ids = []
        for i in range(4):
            job_id = self.get_new_job()
            job_ids.append(job_id)
            time.sleep(4)

        for job_id in job_ids:
            self.assertTrue(job_id in self.client.easy_list('jobs'))

    def testListTask(self):
        job_id = self.get_new_job()
        
        marker = ''
        max_item = 100
        round = 1
        
        while marker or round == 1:
            round += 1
            response = self.client.list_tasks(job_id, marker, 1)
            maker = response.NextMarker
            for task in response.Items:
                self.assertEqual(task.TaskName, 'Map') 

    def testGetTask(self):
        job_id = self.get_new_job()
        task_info = self.client.get_task(job_id, 'Map')

        self.assertEqual(task_info.TaskName, 'Map')
        self.assertEqual(task_info.State, 'Waiting')
        self.assertEqual(task_info.InstanceMetrics.WaitingCount, 3)

    def testGetInstance(self):
        job_id = self.get_new_job()

        for instance_id in range(3):
            instance_info = self.client.get_instance(job_id, 'Map', instance_id)
            self.assertEqual(instance_info.InstanceId, instance_id)
            self.assertEqual(instance_info.State, 'Waiting')

    def testListInstance(self):
        job_id = self.get_new_job()
        
        marker = 0 
        max_item = 100
        round = 1
        
        instances = 0
        while marker or round == 1:
            round += 1
            task_name = 'Map'
            response = self.client.list_instances(job_id, 'Map', marker, 1)
            
            marker = response.NextMarker
            instances += len(response.Items)
        self.assertEqual(instances, 3)


if __name__ == '__main__':
    unittest.main()
