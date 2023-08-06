# botor
A thin wrapper around boto3

## features

 - intelligent connection caching.
 - rate limit handling, with exponential backoff.
 - multi-account sts:assumerole abstraction.

## Example

    from botor.aws.sqs import get_queue, get_messages
    conn_details = {
        'account_number': '111111111111',
        'assume_role': 'MyRole',
        'session_name': 'MySession',
        'region': 'us-east-1'
    }
    queue = get_queue(queue_name='MyQueue', **conn_details)
    messages = get_messages(queue=queue)
