# -*- coding: utf-8 -*-
import ds18b20

c = ds18b20.Check()
c.w1_config()
c.w1_modules()
c.prepare()
