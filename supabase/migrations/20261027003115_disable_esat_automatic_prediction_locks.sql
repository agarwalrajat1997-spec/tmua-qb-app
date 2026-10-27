-- Guarantee snapshots are handled manually outside the student portal.
-- Retain historical records and the job definition, but stop automatic freezing.
select cron.alter_job(job_id := jobid, active := false)
from cron.job
where jobname = 'esat-lock-module-predictions';
