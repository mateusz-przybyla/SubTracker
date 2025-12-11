import workers.scheduler as sched

from api.tasks import reminder_tasks, report_tasks

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
    mocker.patch.object(sched.scheduler, "get_jobs", return_value=[])
    schedule_mock = mocker.patch.object(sched.scheduler, "schedule")

    sched.register_report_job()

    schedule_mock.assert_called_once()

    _, kwargs = schedule_mock.call_args

    assert kwargs['id'] == "monthly_report_job"
    assert kwargs['func'] == report_tasks.generate_monthly_report
    assert kwargs['queue_name'] == "reports"
    assert kwargs['interval'] == 2592000

def test_register_report_job_skips_if_exists(mocker):
    fake_job = mocker.Mock(id="monthly_report_job")
    mocker.patch.object(sched.scheduler, "get_jobs", return_value=[fake_job])
    schedule_mock = mocker.patch.object(sched.scheduler, "schedule")

    sched.register_report_job()

    schedule_mock.assert_not_called()

def test_register_jobs_calls_both(mocker):
    reminder_mock = mocker.patch.object(sched, "register_reminder_job")
    report_mock = mocker.patch.object(sched, "register_report_job")

    sched.register_jobs()

    reminder_mock.assert_called_once()
    report_mock.assert_called_once()