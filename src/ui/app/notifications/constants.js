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

import IC_ARROW_BACK_48PX from 'material-design-icons/navigation/svg/production/ic_arrow_back_48px.svg';
import IC_NOTIFICATIONS_48PX from 'material-design-icons/social/svg/production/ic_notifications_48px.svg';
import IC_PLAY_CIRCLE_OUTLINE_48PX from 'material-design-icons/av/svg/production/ic_play_circle_outline_48px.svg';
import IC_PUBLIC_48PX from 'material-design-icons/social/svg/production/ic_public_48px.svg';
import IC_REMOVE_CIRCLE_OUTLINE_48PX from 'material-design-icons/content/svg/production/ic_remove_circle_outline_48px.svg';
import IC_SETTINGS_48PX from 'material-design-icons/action/svg/production/ic_settings_48px.svg';

const constants = {
    icons: {
        IC_ARROW_BACK_48PX,
        IC_NOTIFICATIONS_48PX,
        IC_PLAY_CIRCLE_OUTLINE_48PX,
        IC_PUBLIC_48PX,
        IC_REMOVE_CIRCLE_OUTLINE_48PX,
        IC_SETTINGS_48PX
    },
    NotificationIconLookup: {
        User: IC_PUBLIC_48PX,

        namespace: IC_PUBLIC_48PX,
        deploy: IC_PLAY_CIRCLE_OUTLINE_48PX,
        delete: IC_REMOVE_CIRCLE_OUTLINE_48PX
    }
};

export default constants;
