import time

import boto.ec2


def get_ec2_connection(aws_conf):
    '''Connect to AWS EC2.
    
    Args:
        aws_conf (deploy_utils.config.DefaultConfig): Configuration vals for AWS.
    
    Returns:
        boto.ec2.connection.EC2Connection: Connection to region.
    '''
    
    print('Connecting to AWS')
    return boto.ec2.connect_to_region(aws_conf.get('region'),
                                      aws_access_key_id=aws_conf.get('aws_access_key_id'),
                                      aws_secret_access_key=aws_conf.get('aws_secret_access_key'))
    
    
def launch_new_ec2(aws_conf, return_connection=False):
    '''Launch a new EC2 instance installing an OBA instance
    
    Args:
        aws_conf (deploy_utils.config.DefaultConfig): Configuration vals for AWS.
        return_connection (boolean, default=False): true to return both the instance and the connection
    
    Returns:
        varies: either the instance that was launched.
            or
            the instance that was launched and the ec2 connection
    '''
    
    conn = get_ec2_connection(aws_conf)
    
    print('Preparing volume')
    block_device = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
    block_device.size = aws_conf.get('volume_size')
    block_device.delete_on_termination = True
    block_device_map = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    block_device_map[aws_conf.get('block_device_map')] = block_device 
    
    print('Launching new instance')
    reservation = conn.run_instances(aws_conf.get('ami_id'),
                                     instance_type=aws_conf.get('instance_type'),
                                     key_name=aws_conf.get('key_pair_name'),
                                     security_groups=aws_conf.get('security_groups').split(','),
                                     block_device_map=block_device_map)
    
    # Get the instance
    instance = reservation.instances[0]
    
    # Check if it's up and running a specified maximum number of times
    max_retries = 10
    num_retries = 0
    
    # Check up on its status every so often
    status = instance.update()
    while status == 'pending':
        if num_retries > max_retries:
            tear_down(instance.id, conn)
            raise Exception('Maximum Number of Instance Retries Hit.  Did EC2 instance spawn correctly?')
        num_retries += 1 
        print('Instance pending, waiting 10 seconds...')
        time.sleep(10)
        status = instance.update()
    
    if status == 'running':
        instance.add_tag("Name", aws_conf.get('instance_name'))
    else:
        print('Instance status: ' + status)
        return None
    
    if return_connection:
        return instance, conn
    else:
        return instance


def tear_down(instance_id, conn):
    '''Terminates a EC2 instance and deletes all associated volumes.
    
    Args:
        instance_id (string): The ec2 instance id to terminate.
        conn (boto.ec2.connection.EC2Connection): Connection to region.
    '''
    
    print('Terminating instance')
    conn.terminate_instances([instance_id])
