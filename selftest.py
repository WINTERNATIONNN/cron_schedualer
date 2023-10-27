# Consult Options.py/CasingTypeEnum.py/DescriptionTypeEnum.py for more info
from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor,ExpressionSchedular
import datetime
from datetime import date
import json

f = open('test.json',)
iflow_expression= json.loads(f.read())["iflow_list"]
# descriptor = ExpressionDescriptor(
#     expression =  "*/5 15 * * THU",
#     casing_type = CasingTypeEnum.Sentence,
#     use_24hour_time_format = True
# )
list = []

for iflow in iflow_expression:
    print(iflow)
    sched = ExpressionSchedular(iflow["cron"], qt = datetime.date(2023,10,26))
    list.append([i.strftime("%H:%M") for i in sched.get_schedule_timetable()])
with open('output.txt', 'w') as f:
    for line in list:
        f.write("%s\n" % line)
# GetDescription uses DescriptionTypeEnum.FULL by default:

# Or passing Options class as second argument:

# options = Options()
# options.casing_type = CasingTypeEnum.Sentence
# options.use_24hour_time_format = True
# descriptor = ExpressionDescriptor("0 23 ? * MON-FRI", options)
# #parser = ExpressionParser("*/10 * * * *", options)
#print(descriptor.get_description(DescriptionTypeEnum.FULL))


