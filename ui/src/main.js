/*
 * Copyright (C) 2020 Nethesis S.r.l.
 * http://www.nethesis.it - nethserver@nethesis.it
 *
 * This script is part of NethServer.
 *
 * NethServer is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License,
 * or any later version.
 *
 * NethServer is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NethServer.  If not, see COPYING.
 */

import Vue from 'vue'
import VueI18n from "vue-i18n"
import Router from 'vue-router'
import VueToggleButton from 'vue-js-toggle-button';
import DocInfo from "./directives/DocInfo.vue";
import VueGoodTable from "vue-good-table";

import "v-suggestions/dist/v-suggestions.css";
import VueSuggestions from 'v-suggestions';

import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import IpBlacklist from './views/IpBlacklist.vue'
import DnsBlacklist from './views/DnsBlacklist.vue'
import Analysis from './views/Analysis.vue'
import Logs from './views/Logs.vue'
import About from './views/About.vue'
import "./filters/filters"
import 'vue-good-table/dist/vue-good-table.css'

window.moment = require("moment");
window.c3 = require('c3');

Vue.config.productionTip = false
Vue.use(VueToggleButton);
Vue.use(VueGoodTable);
Vue.component('doc-info', DocInfo);
Vue.component('suggestions', VueSuggestions);

import UtilService from "./services/util"
Vue.mixin(UtilService)

Vue.use(VueI18n)
const i18n = new VueI18n();

Vue.use(Router)
const router = new Router({
    mode: 'hash',
    base: process.env.BASE_URL,
    routes: [
      { path: '/', redirect: '/dashboard'},
      { path: '/dashboard', component: Dashboard },
      { path: '/ip_blacklist', component: IpBlacklist },
      { path: '/dns_blacklist', component: DnsBlacklist },
      { path: '/analysis', component: Analysis },
      { path: '/logs', component: Logs },
      { path: '/about', name: 'about', component: About },
      { path: "*", redirect: "/" }
    ]
})
router.replace("/dashboard")

var app = new Vue({
    i18n,
    router,
    render: h => h(App)
})

nethserver.fetchTranslatedStrings(function (data, lang) {
    var langCode = lang.substr(0, 2);
    i18n.setLocaleMessage(langCode, data);
    i18n.locale = langCode;
    moment.locale(langCode);
    app.currentLocale = langCode;
    app.$mount('#app'); // Start VueJS application after language strings are loaded
})
