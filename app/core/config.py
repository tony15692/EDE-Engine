from .models import Actor, Capacity

ACTORS=[Actor('Applicant','External actor',True),Actor('Intake','Frontline intake',True),Actor('Agency','Regulatory agency',True),Actor('Reviewer','Specialist reviewer',True),Actor('Supervisor','Supervisory reviewer',True),Actor('ExternalService','External verification service',True)]
CAPACITIES={
'Applicant':Capacity('Applicant',1200,.85),'Intake':Capacity('Intake',360,.85),'Agency':Capacity('Agency',480,.85),
'Reviewer':Capacity('Reviewer',300,.85),'Supervisor':Capacity('Supervisor',240,.85),'ExternalService':Capacity('ExternalService',900,.85)}
