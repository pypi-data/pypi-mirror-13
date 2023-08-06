import re
import os
import sys


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

ICONS = {
    'aws_elb': 'Compute_ElasticLoadBalancing.png',
    'aws_iam_instance_profile': 'Security-Identity_AWSIAM.png',
    'aws_iam_role_policy': '',
    'aws_iam_role': 'Security-Identity_AWSIAM_role.png',
    'aws_instance': 'Compute_AmazonEC2_instance.png',
    'aws_route53_record': 'Networking_AmazonRoute53.png',
    'aws_security_group': '',
}


def repl_func(matchobj):
    resource_type = matchobj.group(2)
    icon = ICONS.get(resource_type)
    if icon is None:
        sys.stderr.write('Unknown resource: {}\n'.format(resource_type))
    if not icon:
        return matchobj.group(0)

    return (
        'label = <<TABLE BORDER="0"><TR><TD><IMG SRC="{1}"/></TD><TD>{0}</TD></TR></TABLE>>,'
        .format(
            matchobj.group(1),
            os.path.join(BASE_DIR, 'icons', icon),
        )
    )


def main():
    text = sys.stdin.read()

    new_text = re.sub(r'label = "((aws_.+)\..+)",', repl_func, text)

    sys.stdout.write(new_text)


if __name__ == '__main__':
    main()
