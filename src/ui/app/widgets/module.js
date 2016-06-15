/*
Copyright 2016 ElasticBox All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

import 'angular-material/angular-material';
import 'angular-vs-repeat';

import coreModule from 'core/module';

import ConfirmDialogService from './confirm-dialog.service';

import AvatarDirective from './ek-avatar/ek-avatar.directive';
import ButtonGroupDirective from './ek-button-group/ek-button-group.directive';
import ConfirmDirective from './ek-confirm/ek-confirm.directive';
import ContainerStateDirective from './ek-container-state/ek-container-state.directive';
import DonutChartDirective from './ek-donut-chart/ek-donut-chart.directive';
import DropDirective from './ek-drop/ek-drop.directive';
import DropContentDirective from './ek-drop/ek-drop-content.directive.js';
import DropTargetDirective from './ek-drop/ek-drop-target.directive.js';
import HeaderDirective from './ek-header/ek-header.directive';
import IkonDirective from './ek-ikon/ek-ikon.directive';
import InkRippleDirective from './ek-ink-ripple/ek-ink-ripple.directive';
import InsertEmailsDirective from './ek-insert-emails/ek-insert-emails.directive';
import InsertLabelsDirective from './ek-insert-labels/ek-insert-labels.directive';
import InstanceNameDirective from './ek-instance-name/ek-instance-name.directive';
import InstanceStateDirective from './ek-instance-state/ek-instance-state.directive';
import LabelEditorDirective from './ek-label-editor/ek-label-editor.directive';
import LabelDirective from './ek-label/ek-label.directive';
import LabelsDirective from './ek-labels/ek-labels.directive';
import NamespaceSelectorDirective from './ek-namespaces-selector/ek-namespace-selector.directive';
import BannerDirective from './ek-banner/ek-banner.directive';
import OwnersSelectorDirective from './ek-owners-selector/ek-owners-selector.directive';
import SearchFilterDirective from './ek-search-filter/ek-search-filter.directive';
import SelectUsersDirective from './ek-select-users/ek-select-users.directive';
import TableDirective from './ek-table/ek-table.directive';
import TableCellDirective from './ek-table/ek-table-cell.directive';
import UserInfoDirective from './ek-user-info/ek-user-info.directive';

const moduleName = 'app.widgets';

angular
    .module(moduleName, [
        coreModule,
        'ngMaterial',
        'vs-repeat'
    ])
    .service('confirmDialog', ConfirmDialogService)

    .directive('ekAvatar', () => new AvatarDirective())
    .directive('ekButtonGroup', () => new ButtonGroupDirective())
    .directive('ekConfirm', ($compile, $rootScope) => {
        'ngInject';

        return new ConfirmDirective($compile, $rootScope);
    })
    .directive('ekContainerState', () => new ContainerStateDirective())
    .directive('ekDrop', () => new DropDirective())
    .directive('ekDropContent', () => new DropContentDirective())
    .directive('ekDropTarget', () => new DropTargetDirective())
    .directive('ekDonutChart', () => new DonutChartDirective())
    .directive('ekHeader', () => new HeaderDirective())
    .directive('ekIkon', () => new IkonDirective())
    .directive('ekInkRipple', ($timeout) => {
        'ngInject';

        return new InkRippleDirective($timeout);
    })
    .directive('ekInsertEmails', () => new InsertEmailsDirective())
    .directive('ekInsertLabels', () => new InsertLabelsDirective())
    .directive('ekLabel', () => new LabelDirective())
    .directive('ekLabelEditor', () => new LabelEditorDirective())
    .directive('ekLabels', () => new LabelsDirective())
    .directive('ekInstanceName', () => new InstanceNameDirective())
    .directive('ekInstanceState', () => new InstanceStateDirective())
    .directive('ekNamespaceSelector', () => new NamespaceSelectorDirective())
    .directive('ekBanner', () => new BannerDirective())
    .directive('ekOwnersSelector', () => new OwnersSelectorDirective())
    .directive('ekSearchFilter', () => new SearchFilterDirective())
    .directive('ekSelectUsers', () => new SelectUsersDirective())
    .directive('ekTable', () => new TableDirective())
    .directive('ekTableCell', () => new TableCellDirective())
    .directive('ekUserInfo', () => new UserInfoDirective());

export default moduleName;
