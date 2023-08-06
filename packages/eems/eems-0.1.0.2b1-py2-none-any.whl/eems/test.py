# -*- coding: utf-8 -*-
import ds18b20

t = ds18b20.Temp(console=True, csv=True)
t.monitor(duration=10)
