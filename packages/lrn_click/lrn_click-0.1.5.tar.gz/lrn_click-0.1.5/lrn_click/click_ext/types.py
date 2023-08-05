import click


class AlphaNumParamType(click.ParamType):
    "Alphanumeric Click parameter type"
    name = "alphanumeric"

    def convert(self, value, param, ctx):
        if isinstance(value, str) and value.isalnum():
            return value

        self.fail(
            "{} contains non-alphanumeric characters".format(value),
            param,
            ctx
        )


class AWSRegionParamType(click.ParamType):
    "AWS Region parameter type"
    name = "region_name"

    def convert(self, value, param, ctx):
        regions = param.prompt_list_func(ctx)

        if value and isinstance(value, str):
            # look up string region
            matches = [r for r in regions.values() if r == value]
            res = matches.pop() if len(matches) == 1 else None

            if not res:
                self.fail(
                    "Region not found in ['{}']".format(
                        "','".join(regions)
                    ),
                    param,
                    ctx
                )

            value = res

            # setup boto connection for other usage in the context
            try:
                from boto3.session import Session
                ctx.obj['session'] = Session(region_name=value)

            except ImportError:
                raise click.exceptions.ClickError("Missing boto3 dependancy")

        return value


class VpcPrefixParamType(click.ParamType):
    "VPC prefix parameter type"
    name = "vpc_prefix"

    def convert(self, value, param, ctx):
        if isinstance(value, str) and not value.isalnum():
            self.fail("Prefix contains non-alphanumeric character!", param, ctx)

        if value:
            ec2_client = ctx.obj['session'].client('ec2')
            res = ec2_client.describe_vpcs(
                Filters=[{'Name': 'tag:Name', 'Values': [value]}]
            )

            if res.get("Vpcs"):
                if param.unique:
                    self.fail(
                        "VPC '{}' already exists!".format(value), param, ctx
                    )
            elif not param.unique:
                self.fail("VPC '{}' doesn't exist!".format(value), param, ctx)

        return value


class VpcNumOfAZsParamType(click.IntRange):
    "VPC AZ coverage parameter type"
    name = "number_of_azs"

    def convert(self, value, param, ctx):
        ec2_client = ctx.obj['session'].client('ec2')
        azs = ec2_client.describe_availability_zones()
        azs = azs.get('AvailabilityZones')

        available_azs = [
            az.get('ZoneName') for az in azs if az.get('State') == 'available'
        ]

        self.min = 1
        self.max = len(available_azs)

        return super().convert(value, param, ctx)


class VpcCIDRParamType(click.ParamType):
    "VPC CIDR parameter type"
    name = "cidr"

    def convert(self, value, param, ctx):
        from iptools.ipv4 import validate_cidr, long2ip, cidr2block

        if isinstance(value, str) and not validate_cidr(value):
            self.fail("CIDR is not valid!", param, ctx)

        elif isinstance(value, str):
            layer_mask = int(param.layer_mask)
            num_of_layers = int(param.num_of_layers)

            # calculate a single layer's mask size
            shift = 32 - layer_mask
            layer_mask = (1 << shift) - 1

            # calculate the whole stacks minimum required cidr
            stack_mask = ~layer_mask * \
                (num_of_layers * ctx.params.get('azs'))
            stack_cidr = 32 - len(bin(~stack_mask & 0xFFFFFFFF)[2:])

            try:
                (vpc_ip, vpc_cidr) = value.split('/')
                vpc_cidr = int(vpc_cidr)

                if vpc_cidr > stack_cidr:
                    self.fail(
                        "CIDR netmask smaller than required for {} layers "
                        "of {} ip addresses. It needs to be at "
                        "least {}.".format(
                            num_of_layers, layer_mask, stack_cidr
                        ),
                        param,
                        ctx
                    )

                (start_ip, end_ip) = cidr2block(value)
                shift = 32 - int(vpc_cidr)
                vpc_mask = (1 << shift) - 1
                vpc_netmask = long2ip(~vpc_mask & 0xFFFFFFFF)

                return {
                    'cidr': "/".join([start_ip, str(vpc_cidr)]),
                    'start_ip': start_ip,
                    'end_ip': end_ip,
                    'netmask': vpc_netmask
                }

            except (ValueError, AttributeError) as e:
                raise click.UsageError(e)


class VpcKeyPairParamType(click.ParamType):
    "VPC key pair parameter type"
    name = "vpc_keypair"

    def convert(self, value, param, ctx):
        from lrn_click.utils import get_keypairs

        if isinstance(value, str) and value:
            key_pairs = get_keypairs(ctx)
            if value not in key_pairs:
                self.fail(
                    "Key pair not found in ['{}']".format(
                        "','".join(key_pairs)),
                    param,
                    ctx
                )

        return value
