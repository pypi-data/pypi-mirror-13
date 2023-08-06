# (c) Copyright [2015] Hewlett Packard Enterprise Development LP
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from django.conf.urls import patterns
from django.conf.urls import url

from horizon_hpe_storage.storage_panel.diags import views

VIEWS_MOD = ('horizon_hpe_storage.storage_panel.diags.views')

urlpatterns = patterns(
    VIEWS_MOD,
    url(r'^$',
        views.IndexView.as_view(),
        name='index'),
    url(r'^(?P<test_name>[^/]+)/run_test/$',
        views.RunTestView.as_view(),
        name='run_test'),
    url(r'^create_test/$',
        views.CreateTestView.as_view(),
        name='create_test'),
    url(r'^(?P<test_name>[^/]+)/edit_test/$',
        views.EditTestView.as_view(),
        name='edit_test'),
    url(r'^(?P<test_name>[^/]+)/$',
        views.DetailView.as_view(),
        name='detail'),
)
