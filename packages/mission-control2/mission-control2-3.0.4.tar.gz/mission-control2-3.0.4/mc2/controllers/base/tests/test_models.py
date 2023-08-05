import json
import pytest
import responses

from mock import patch

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from mc2.controllers.base.tests.base import ControllerBaseTestCase
from mc2.controllers.base.models import Controller, publish_to_websocket
from mc2.controllers.base import exceptions

from ws4redis.publisher import RedisPublisher


# test models for polymorphic
class SubTypeA(Controller):
            pass


class SubTypeB(Controller):
    pass


@pytest.mark.django_db
class ModelsTestCase(ControllerBaseTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        post_save.disconnect(publish_to_websocket, sender=Controller)
        self.maxDiff = None

    def test_get_marathon_app_data(self):
        controller = self.mk_controller()
        self.assertEquals(controller.get_marathon_app_data(), {
            "id": controller.app_id,
            "cpus": 0.1,
            "mem": 128.0,
            "instances": 1,
            "cmd": "ping",
        })

    @responses.activate
    def test_update_marathon_marathon_exception(self):
        controller = self.mk_controller()
        self.mock_update_marathon_app(controller.app_id, 404)
        with self.assertRaises(exceptions.MarathonApiException):
            controller.update_marathon_app()

    @responses.activate
    def test_restart_marathon_marathon_exception(self):
        controller = self.mk_controller()
        self.mock_restart_marathon_app(controller.app_id, 404)
        with self.assertRaises(exceptions.MarathonApiException):
            controller.marathon_restart_app()

    @responses.activate
    def test_delete_marathon_marathon_exception(self):
        controller = self.mk_controller()
        self.mock_delete_marathon_app(controller.app_id, 404)
        with self.assertRaises(exceptions.MarathonApiException):
            controller.marathon_destroy_app()

    @responses.activate
    def test_marathon_app_exists(self):
        controller = self.mk_controller()

        self.mock_exists_on_marathon(controller.app_id)
        self.assertTrue(controller.exists_on_marathon())

    @responses.activate
    def test_marathon_app_does_not_exist(self):
        controller = self.mk_controller()

        self.mock_exists_on_marathon(controller.app_id, 404)
        self.assertFalse(controller.exists_on_marathon())

    @responses.activate
    def test_get_state_display(self):
        controller = self.mk_controller()
        self.assertEquals(controller.get_state_display(), 'Initial')

    @responses.activate
    def test_to_dict(self):
        controller = self.mk_controller()
        self.assertEquals(controller.to_dict(), {
            'id': controller.id,
            'name': 'Test App',
            'app_id': controller.app_id,
            'state': 'initial',
            'state_display': 'Initial',
            'marathon_cmd': 'ping',
        })

    def test_leaf_class_helper(self):
        controller = self.mk_controller()
        self.assertTrue(isinstance(controller, Controller))

        suba = SubTypeA.objects.create(
            name='sub type a', marathon_cmd='pingA', owner=self.user)
        subb = SubTypeB.objects.create(
            name='sub type b', marathon_cmd='pingB', owner=self.user)

        base_suba = Controller.objects.get(pk=suba.pk)
        base_subb = Controller.objects.get(pk=subb.pk)

        self.assertTrue(isinstance(base_suba, SubTypeA))
        self.assertTrue(isinstance(base_subb, SubTypeB))

    def test_publish_to_websocket(self):
        post_save.connect(publish_to_websocket, sender=Controller)
        with patch.object(
                RedisPublisher, 'publish_message', return_value=None
        ) as mock_method:
            controller = self.mk_controller()

        kwargs = {
            "is_created": True,
            "name": "Test App",
            "app_id": controller.app_id,
            "state": "initial",
            "state_display": "Initial",
            "marathon_cmd": "ping",
            "id": controller.id}
        mock_method.assert_called_once_with(json.dumps(kwargs))
