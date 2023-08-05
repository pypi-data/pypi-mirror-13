def get_regions(ctx):
    "Get the AWS regions"
    from botocore.exceptions import NoCredentialsError
    from botocore.exceptions import NoRegionError
    import boto3
    import click

    try:
        ec2 = boto3.client('ec2')
        regions = [
            r.get('RegionName') for r in ec2.describe_regions().get(
                'Regions', {})
        ]

    except NoCredentialsError:
        raise click.exceptions.ClickException("Missing AWS credentials.")

    except NoRegionError:
        raise click.exceptions.ClickException("Missing AWS default region.")

    return sorted(regions)


def get_region_titles(ctx):
    import collections

    region_desc = {
        "ap-northeast-1": "Tokyo",
        "ap-northeast-2": "Seoul",
        "ap-southeast-1": "Singapore",
        "ap-southeast-2": "Sydney",
        "cn-north-1": "China",
        "eu-central-1": "Frankfurt",
        "eu-west-1": "Ireland",
        "sa-east-1": "Sao Paulo",
        "us-east-1": "Virginia",
        "us-west-1": "California",
        "us-west-2": "Oregon"
    }

    regions = {
        "{:<14} ({})".format(region_desc.get(r, '<< unknown >>'), r): r \
        for r in get_regions(ctx)
    }

    return collections.OrderedDict(sorted(regions.items(), key=lambda t: t[1]))


def get_keypairs(ctx):
    "Get the key pairs"
    ec2_client = ctx.obj['session'].client('ec2')
    res = ec2_client.describe_key_pairs()
    return [k.get('KeyName') for k in res.get('KeyPairs', {})]
