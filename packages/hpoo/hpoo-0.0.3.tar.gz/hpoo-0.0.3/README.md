HPOO - Interact with your HPOO v10 instance in your favorite language
=====================================================================

This module allow you to interact easily with HPOO in python

# Installation method

    pip install hpoo

# Usage sample

    from hpoo import HPOO
    oo = HPOO(url="[URL OF YOUR INSTANCE]", user="[USERNAME]", password="[PASS]")
    oo.start_flow(uuid='[FLOW-UUID]', runName='my run', inputs={})
