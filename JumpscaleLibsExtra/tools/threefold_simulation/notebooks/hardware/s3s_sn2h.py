from Jumpscale import j


def bom_calc(environment):

    from hardware.components.components_s3s import bom_populate

    environment.bom = bom_populate(environment.bom)

    # sn1
    environment.device_node_add("compute", template="sn2h", nr=1)
