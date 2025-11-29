import workers.scheduler as sched


def test_register_jobs_adds_job(mocker):
    mocker.patch.object(sched.scheduler, "get_jobs", return_value=[])
    schedule_mock = mocker.patch.object(sched.scheduler, "schedule")

    sched.register_jobs()

    schedule_mock.assert_called_once()
    args, kwargs = schedule_mock.call_args
    assert kwargs['id'] == "subscription_payment_reminder_job"
    assert kwargs['func'] == sched.check_upcoming_payments

def test_register_jobs_skips_if_exists(mocker):
    fake_job = mocker.Mock(id="subscription_payment_reminder_job")
    mocker.patch.object(sched.scheduler, "get_jobs", return_value=[fake_job])
    schedule_mock = mocker.patch.object(sched.scheduler, "schedule")

    sched.register_jobs()

    schedule_mock.assert_not_called()