#!/usr/bin/env python

from lib import Ep3000


status = Ep3000.StatusCommand()

print status.send()
