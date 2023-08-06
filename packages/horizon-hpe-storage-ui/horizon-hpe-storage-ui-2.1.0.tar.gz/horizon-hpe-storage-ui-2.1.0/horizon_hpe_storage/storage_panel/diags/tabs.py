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

from django.utils.translation import ugettext_lazy as _

from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Test Results")
    slug = "overview"
    template_name = ("diags/_detail_overview.html")

    def get_context_data(self, request):
        return {"test": self.tab_group.kwargs['test']}


class SystemInfoTab(tabs.Tab):
    name = _("Storage System Information")
    slug = "systems"
    template_name = ("diags/_system_overview.html")

    def get_context_data(self, request):
        return {"test": self.tab_group.kwargs['test']}


class TestDetailTabs(tabs.TabGroup):
    slug = "test_details"
    # tabs = (OverviewTab, SystemInfoTab)
    # only show test results. System info has its own panel.
    # but keep around as example of having tabbed detail panel
    tabs = (OverviewTab,)
