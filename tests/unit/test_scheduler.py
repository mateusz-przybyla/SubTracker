import workers.scheduler as sched

from api.tasks import reminder_tasks, report_tasks
from api.infra.queues import get_report_queue

def test_register_reminder_job_adds_job(mocker):
    mocker.patch.object(sched.scheduler, "get_jobs", return_value=[])
    schedule_mock = mocker.patch.object(sched.scheduler, "schedule")

    sched.register_reminder_job()

    schedule_mock.assert_called_once()

    _, kwargs = schedule_mock.call_args

    assert kwargs['id'] == "subscription_payment_reminder_job"
    assert kwargs['func'] is reminder_tasks.check_upcoming_payments
    assert kwargs['queue_name'] == "reminders"
    assert kwargs['repeat'] is None
    assert kwargs['interval'] == 86400

def test_register_reminder_job_skips_if_exists(mocker):
    fake_job = mocker.Mock(id="subscription_payment_reminder_job")
    mocker.patch.object(sched.scheduler, "get_jobs", return_value=[fake_job])
    schedule_mock = mocker.patch.object(sched.scheduler, "schedule")

    sched.register_reminder_job()

    schedule_mock.assert_not_called()

def test_register_report_job_adds_job(mocker):
    # arrange: Redis says - job does NOT exist
    exists_mock = mocker.patch.object(
        sched.scheduler.connection,
        "exists",
        return_value=False
    )
    cron_mock = mocker.patch.object(sched.scheduler, "cron")

    # act
    sched.register_report_job()

    # assert
    exists_mock.assert_called_once_with("rq:scheduler:job:monthly_report_job")
    cron_mock.assert_called_once()

    _, kwargs = cron_mock.call_args

    assert kwargs['id'] == "monthly_report_job"
    assert kwargs['func'] == report_tasks.generate_monthly_report
    assert kwargs['queue_name'] == get_report_queue().name
    assert kwargs['cron_string'] == "0 0 1 * *"
    assert kwargs['use_local_timezone'] is True

def test_register_report_job_skips_if_exists(mocker):
    # arrange: Redis says - job EXISTS
    exists_mock = mocker.patch.object(
        sched.scheduler.connection,
        "exists",
        return_value=True
    )
    cron_mock = mocker.patch.object(sched.scheduler, "cron")

    # act
    sched.register_report_job()

    # assert
    exists_mock.assert_called_once_with("rq:scheduler:job:monthly_report_job")
    cron_mock.assert_not_called()

def test_register_jobs_calls_both(mocker):
    reminder_mock = mocker.patch.object(sched, "register_reminder_job")
    report_mock = mocker.patch.object(sched, "register_report_job")

    sched.register_jobs()

    reminder_mock.assert_called_once()
    report_mock.assert_called_once()