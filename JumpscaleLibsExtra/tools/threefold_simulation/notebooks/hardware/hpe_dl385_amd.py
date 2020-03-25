from Jumpscale import j


def bom_calc(bom, environment):

    raise RuntimeError("to be implemented")
    assert len(bom.components) == 0

    bom.components.new(
        name="s1",
        description="HPE DL385 AMD, 12 HD's fit inside, 10 gbit dual",
        cost=3200,
        rackspace_u=2,
        cru=0,
        sru=0,
        hru=0,
        mru=0,
        su_perc=50,
        cu_perc=50,
        power=150,
    )

    bom.components.new(name="margin", description="margin per node for threefold and its partners", power=0, cost=500)

    bom.components.new(
        name="hd12", description="HPE Helium 12TB (6-8 watt)", cost=734, hru=12000, power=10, su_perc=100
    )
    bom.components.new(
        name="amd1",
        description="AMD-EPYC-7351 @ 2.40GHz (32 logical cores)",
        cost=920,
        cru=32,
        power=150,
        cu_perc=100,
        passmark=18140,
    )

    bom.components.new(name="ssd1", description="1.92 TB HPE SSD", cost=1022, sru=1920, power=10, su_perc=100)
    bom.components.new(name="mem32_ecc", description="mem 32", cost=320, mru=32, power=8, cu_perc=100)

    bom.components.new(
        name="ng2",
        description="48 ports 10 gbit + 4 ports 10 gbit sfp: fs.com + cables",
        cost=4500,
        power=100,
        rackspace_u=1,
    )

    # create the template for dc1
    d = bom.devices.new(name="server")
    d.components.new(name="s1", nr=1)
    d.components.new(name="amd1", nr=2)
    d.components.new(name="hd12", nr=8)
    d.components.new(name="mem32_ecc", nr=16)
    d.components.new(name="ssd1", nr=4)

    d = bom.devices.new(name="switch")
    d.components.new(name="ng2", nr=1)

    environment.devices.clear()

    # see the bill of material sheet to define the devices
    server = bom.device_get("server", device_template_name="server", environment=environment)
    # the switch added to the node
    switch = bom.device_get("switch", device_template_name="switch", environment=environment)

    # an environment to simulate the overhead per node (eg. 1 switch per node)
    environment.device_node_add("server", server, 20)
    environment.device_overhead_add("switch", switch, 2)

    return bom, environment
