<!--
#
# Copyright (C) 2020 Nethesis S.r.l.
# http://www.nethesis.it - nethserver@nethesis.it
#
# This script is part of NethServer.
#
# NethServer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or any later version.
#
# NethServer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NethServer.  If not, see COPYING.
#
-->

<template>
  <div>
    <h2>{{$t('analysis.title')}}</h2>
    <div v-show="!isLoaded.config" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-show="isLoaded.config">
      <h3 v-if="ipConfig.status && !dnsConfig.status">{{$t('analysis.check_ip_address')}}</h3>
      <h3 v-else-if="!ipConfig.status && dnsConfig.status">{{$t('analysis.check_domain')}}</h3>
      <h3 v-else>{{$t('analysis.check_ip_address_or_domain')}}</h3>
      <!-- cannot search banner -->
      <div v-if="!ipConfig.status && !dnsConfig.status" class="alert alert-info alert-dismissable">
        <span class="pficon pficon-info"></span>
        <span>{{$t('analysis.cannot_search')}}</span>
      </div>
      <!-- IP search -->
      <form
        v-show="ipConfig.status && !dnsConfig.status"
        class="form-horizontal"
        v-on:submit.prevent="validateSearchIp()"
      >
        <div :class="['form-group', {'has-error': error.ipSearch}]">
          <label class="col-sm-2 control-label" for="ip-search">
            {{$t('analysis.ip_address')}}
            <doc-info :placement="'bottom'" :chapter="'search_ip_address'" :inline="true"></doc-info>
          </label>
          <div class="col-sm-3">
            <input
              type="text"
              v-model="ipSearch"
              id="ip-search"
              ref="ipSearch"
              class="form-control"
            />
            <span
              v-if="error.ipSearch"
              class="help-block"
            >{{$t('validation.ip_search_' + error.ipSearch)}}</span>
          </div>
        </div>
        <!-- check IP button -->
        <div class="form-group">
          <label class="col-sm-2 control-label label-loader">
            <div
              v-if="!isLoaded.search"
              class="spinner spinner-sm form-spinner-loader adjust-top-loader"
            ></div>
          </label>
          <span class="col-sm-2">
            <button
              class="btn btn-primary"
              type="submit"
              :disabled="!isLoaded.search"
            >{{$t('analysis.check')}}</button>
          </span>
        </div>
      </form>
      <!-- Domain search -->
      <form
        v-show="!ipConfig.status && dnsConfig.status"
        class="form-horizontal"
        v-on:submit.prevent="validateSearchDomain()"
      >
        <div :class="['form-group', {'has-error': error.domainSearch}]">
          <label class="col-sm-2 control-label" for="domain-search">
            {{$t('analysis.domain')}}
            <doc-info :placement="'bottom'" :chapter="'search_domain'" :inline="true"></doc-info>
          </label>
          <div class="col-sm-3">
            <input
              type="text"
              v-model="domainSearch"
              id="domain-search"
              ref="domainSearch"
              class="form-control"
            />
            <span
              v-if="error.domainSearch"
              class="help-block"
            >{{$t('validation.domain_search_' + error.domainSearch)}}</span>
          </div>
        </div>
        <!-- check domain button -->
        <div class="form-group">
          <label class="col-sm-2 control-label label-loader">
            <div
              v-if="!isLoaded.search"
              class="spinner spinner-sm form-spinner-loader adjust-top-loader"
            ></div>
          </label>
          <span class="col-sm-2">
            <button
              class="btn btn-primary"
              type="submit"
              :disabled="!isLoaded.search"
            >{{$t('analysis.check')}}</button>
          </span>
        </div>
      </form>
      <!-- IP or domain search -->
      <form
        v-show="(ipConfig.status && dnsConfig.status) || (!ipConfig.status && !dnsConfig.status)"
        class="form-horizontal"
        v-on:submit.prevent="validateSearchIpOrDomain()"
      >
        <div :class="['form-group', {'has-error': error.ipOrDomainSearch}]">
          <label class="col-sm-2 control-label" for="ip-domain-search">
            {{$t('analysis.ip_or_domain')}}
            <doc-info :placement="'bottom'" :chapter="'search_ip_or_domain'" :inline="true"></doc-info>
          </label>
          <div class="col-sm-3">
            <input
              type="text"
              v-model="ipOrDomainSearch"
              id="ip-domain-search"
              ref="ipOrDomainSearch"
              class="form-control"
              :disabled="!ipConfig.status && !dnsConfig.status"
            />
            <span
              v-if="error.ipOrDomainSearch"
              class="help-block"
            >{{$t('validation.ip_or_domain_search_' + error.ipOrDomainSearch)}}</span>
          </div>
        </div>
        <!-- check IP or domain button -->
        <div class="form-group">
          <label class="col-sm-2 control-label label-loader">
            <div
              v-if="!isLoaded.search"
              class="spinner spinner-sm form-spinner-loader adjust-top-loader"
            ></div>
          </label>
          <span class="col-sm-2">
            <button
              class="btn btn-primary"
              type="submit"
              :disabled="!isLoaded.search || (!ipConfig.status && !dnsConfig.status)"
            >{{$t('analysis.check')}}</button>
          </span>
        </div>
      </form>
    </div>
    <!-- logs -->
    <h3>{{$t('analysis.recent_logs')}}</h3>
    <form class="form-horizontal" v-on:submit.prevent="getLogs()">
      <!-- logs type -->
      <div class="form-group">
        <label class="col-sm-2 control-label" for="logs-type">{{$t('analysis.logs')}}</label>
        <div class="col-sm-3">
          <select
            class="combobox form-control"
            v-model="logsType"
            :disabled="!dnsConfig.status"
            @change="getLogs()"
            id="logs-type"
          >
            <option value="ip">{{$t('ip_blacklist.title')}}</option>
            <option v-show="dnsConfig.status" value="dns">{{$t('dns_blacklist.title')}}</option>
          </select>
        </div>
      </div>
      <!-- filter -->
      <div class="form-group">
        <label class="col-sm-2 control-label" for="searchFilter">{{$t('analysis.filter')}}</label>
        <div class="col-sm-3">
          <input type="text" v-model="searchFilter" id="searchFilter" class="form-control" />
        </div>
        <!-- clear filter -->
        <span class="col-sm-2 search-filter-btn">
          <button
            class="btn btn-default"
            type="button"
            @click="clearFilter()"
          >{{$t('analysis.clear')}}</button>
        </span>
      </div>
      <!-- number of lines -->
      <div class="form-group">
        <label class="col-sm-2 control-label" for="lines">{{$t('analysis.lines')}}</label>
        <div class="col-sm-2">
          <input
            type="number"
            v-model="lines"
            id="lines"
            min="1"
            class="form-control"
            :placeholder="$t('analysis.lines_placeholder')"
          />
        </div>
      </div>
      <!-- filter button -->
      <div class="form-group">
        <label class="col-sm-2 control-label label-loader"></label>
        <span class="col-sm-2">
          <button
            class="btn btn-primary"
            type="submit"
            :disabled="!isLoaded.logs"
          >{{$t('analysis.search_logs')}}</button>
        </span>
      </div>
    </form>
    <div v-show="!isLoaded.logs" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-show="isLoaded.logs">
      <!-- IP logs -->
      <div v-show="logsType == 'ip'" class="col-sm-12">
        <vue-good-table
          :columns="ipColumns"
          :rows="ipLogs"
          :lineNumbers="false"
          :sort-options="{
            enabled: true,
            initialSortBy: {field: 'seconds', type: 'desc'},
          }"
          :search-options="{
            enabled: false,
          }"
          :pagination-options="{
            enabled: true,
            rowsPerPageLabel: tableLangsTexts.rowsPerPageText,
            nextLabel: tableLangsTexts.nextText,
            prevLabel: tableLangsTexts.prevText,
            ofLabel: tableLangsTexts.ofText,
            dropdownAllowAll: false,
          }"
          styleClass="table condensed responsive vgt2"
        >
          <template slot="table-row" slot-scope="props">
            <span v-if="props.column.field == 'seconds'">
              <span>{{props.row.time}}</span>
            </span>
            <span v-if="props.column.field == 'interface'">
              <span>{{props.row.interface || '-'}}</span>
            </span>
            <span v-if="props.column.field == 'source'">
              <span
                v-if="ipConfig.status"
                data-toggle="tooltip"
                data-placement="top"
                :title="$t('analysis.check_ip_address')"
              >
                <a @click="ipAddressClicked(props.row.source)">{{props.row.source}}</a>
              </span>
              <span v-else>{{props.row.source}}</span>
            </span>
            <span v-if="props.column.field == 'dest'">
              <span
                v-if="ipConfig.status"
                data-toggle="tooltip"
                data-placement="top"
                :title="$t('analysis.check_ip_address')"
              >
                <a @click="ipAddressClicked(props.row.dest)">{{props.row.dest}}</a>
              </span>
              <span v-else>{{props.row.dest}}</span>
            </span>
            <span v-if="props.column.field == 'protocol'">
              <span>{{props.row.protocol || '-'}}</span>
            </span>
            <span v-if="props.column.field == 'dest_port'">
              <span>{{props.row.dest_port || '-'}}</span>
            </span>
            <span v-if="props.column.field == 'dest_service'">
              <span>{{props.row.dest_service || '-'}}</span>
            </span>
          </template>
        </vue-good-table>
      </div>
      <!-- DNS logs -->
      <div v-show="logsType == 'dns'" class="col-sm-12">
        <vue-good-table
          :columns="dnsColumns"
          :rows="dnsLogs"
          :lineNumbers="false"
          :sort-options="{
            enabled: true,
            initialSortBy: {field: 'seconds', type: 'desc'},
          }"
          :search-options="{
            enabled: false,
          }"
          :pagination-options="{
            enabled: true,
            rowsPerPageLabel: tableLangsTexts.rowsPerPageText,
            nextLabel: tableLangsTexts.nextText,
            prevLabel: tableLangsTexts.prevText,
            ofLabel: tableLangsTexts.ofText,
            dropdownAllowAll: false,
          }"
          styleClass="table condensed responsive vgt2"
        >
          <template slot="table-row" slot-scope="props">
            <span v-if="props.column.field == 'seconds'">
              <span>{{props.row.seconds | shortDateFormat}}</span>
            </span>
            <span v-if="props.column.field == 'source'">
              <span>{{props.row.source}}</span>
            </span>
            <span v-if="props.column.field == 'dest'">
              <span
                v-if="dnsConfig.status"
                data-toggle="tooltip"
                data-placement="top"
                :title="$t('analysis.check_domain')"
              >
                <a @click="domainClicked(props.row.dest)">{{props.row.dest}}</a>
              </span>
              <span v-else>{{props.row.dest}}</span>
            </span>
            <span v-if="props.column.field == 'queryStatus.description'">
              <span>{{props.row.queryStatus.description || '-'}}</span>
            </span>
            <span v-if="props.column.field == 'recordType'">
              <span>{{props.row.recordType || '-'}}</span>
            </span>
          </template>
        </vue-good-table>
      </div>
    </div>
    <!-- search result modal -->
    <div class="modal" id="search-result-modal" tabindex="-1" role="dialog" data-backdrop="static">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4
              class="modal-title"
            >{{searchResult.ipAddress ? $t('analysis.check_ip_address') : $t('analysis.check_domain')}}</h4>
          </div>
          <form class="form-horizontal">
            <div class="modal-body">
              <div v-show="!isLoaded.searchModal" class="spinner form-spinner-loader mg-left-sm"></div>
              <div v-show="isLoaded.searchModal">
                <!-- result banner -->
                <div
                  :class="['alert', 'alert-dismissable', searchResult.categories && searchResult.categories.length ? 'alert-warning' : 'alert-info' ]"
                >
                  <span
                    :class="['pficon', searchResult.categories && searchResult.categories.length ? 'pficon-warning-triangle-o' : 'pficon-info']"
                  ></span>
                  <span v-if="searchResult.ipAddress">
                    {{$t('analysis.ip_address')}}
                    <span
                      v-if="searchResult.categories && searchResult.categories.length"
                    >{{ $t('analysis.is_blocked_by_ip_blacklist') }}</span>
                    <span v-else>{{ $t('analysis.is_not_blocked_by_ip_blacklist') }}</span>
                  </span>
                  <span v-else>
                    {{$t('analysis.domain')}}
                    <span
                      v-if="searchResult.categories && searchResult.categories.length"
                    >{{ $t('analysis.is_blocked_by_dns_blacklist') }}</span>
                    <span v-else>{{ $t('analysis.is_not_blocked_by_dns_blacklist') }}</span>
                  </span>
                </div>
                <!-- search results form -->
                <div class="form-group">
                  <label
                    class="col-sm-3 control-label"
                  >{{searchResult.ipAddress ? $t('analysis.ip_address') : $t('analysis.domain')}}</label>
                  <div class="col-sm-9">
                    <span
                      class="search-result"
                    >{{searchResult.ipAddress ? searchResult.ipAddress : searchResult.domain}}</span>
                  </div>
                </div>
                <div class="form-group">
                  <label class="col-sm-3 control-label">{{$t('analysis.blocked_by')}}</label>
                  <div class="col-sm-9">
                    <span class="search-result">
                      <span v-if="searchResult.categories && searchResult.categories.length">
                        <div
                          v-for="(category, index) in searchResult.categories"
                          v-bind:key="index"
                        >{{$te('categories.' + category) ? $t('categories.' + category) : category | prettyString}}</div>
                      </span>
                      <span v-else>{{ $t('analysis.no_category') }}</span>
                    </span>
                  </div>
                </div>
                <div v-if="searchResult.domain">
                  <div class="form-group">
                    <label class="col-sm-3 control-label">{{$t('analysis.blocked_requests')}}</label>
                    <div class="col-sm-9">
                      <span class="search-result">{{searchResult.blockedRequests}}</span>
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="col-sm-3 control-label">{{$t('analysis.total_requests')}}</label>
                    <div class="col-sm-9">
                      <span class="search-result">{{searchResult.totalRequests}}</span>
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="col-sm-3 control-label">{{$t('analysis.requested_by')}}</label>
                    <div class="col-sm-5 clients-list">
                      <span class="search-result">
                        <span v-if="searchResult.clients && searchResult.clients.length">
                          <div
                            v-for="(client, index) in searchResult.clients"
                            v-bind:key="index"
                          >{{client}}</div>
                        </span>
                        <span v-else>{{ $t('analysis.no_client') }}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer no-mg-top">
              <button class="btn btn-primary" type="button" data-dismiss="modal">{{$t('close')}}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Analysis",
  mounted() {
    this.getIpConfig();
  },
  data() {
    return {
      searchFilter: "",
      ipLogs: [],
      dnsLogs: [],
      lines: 1000,
      isLoaded: {
        search: true,
        logs: false,
        config: false,
        searchModal: false
      },
      ipConfig: {
        status: false
      },
      dnsConfig: {
        status: false
      },
      tableLangsTexts: this.tableLangs(),
      ipColumns: [
        {
          label: this.$i18n.t("analysis.time"),
          field: "seconds",
          sortable: true,
          type: "number"
        },
        {
          label: this.$i18n.t("analysis.interface"),
          field: "interface",
          sortable: true
        },
        {
          label: this.$i18n.t("analysis.source"),
          field: "source",
          sortable: true
        },
        {
          label: this.$i18n.t("analysis.destination"),
          field: "dest",
          sortable: true
        },
        {
          label: this.$i18n.t("analysis.protocol"),
          field: "protocol",
          sortable: true
        },
        {
          label: this.$i18n.t("analysis.destination_port"),
          field: "dest_port",
          sortable: true,
          type: "number"
        },
        {
          label: this.$i18n.t("analysis.destination_service"),
          field: "dest_service",
          sortable: true
        }
      ],
      dnsColumns: [
        {
          label: this.$i18n.t("analysis.time"),
          field: "seconds",
          sortable: true,
          type: "number"
        },
        {
          label: this.$i18n.t("analysis.source"),
          field: "source",
          sortable: true
        },
        {
          label: this.$i18n.t("analysis.destination"),
          field: "dest",
          sortable: true
        },
        {
          label: this.$i18n.t("analysis.query_status"),
          field: "queryStatus.description",
          sortable: true
        },
        {
          label: this.$i18n.t("analysis.record_type"),
          field: "recordType",
          sortable: true
        }
      ],
      error: {
        ipSearch: false,
        domainSearch: false,
        ipOrDomainSearch: false
      },
      ipSearch: "",
      domainSearch: "",
      ipOrDomainSearch: "",
      searchResult: {},
      logsType: ""
    };
  },
  methods: {
    getLogs() {
      this.isLoaded.logs = false;
      this.searchFilter = this.searchFilter.trim();
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/analysis/read"],
        {
          action: "logs",
          filter: this.searchFilter,
          lines: this.lines,
          type: this.logsType
        },
        null,
        function(success) {
          success = JSON.parse(success);
          if (context.logsType === "ip") {
            context.ipLogs = success.logs;
          } else {
            context.dnsLogs = success.logs;
          }
          context.isLoaded.logs = true;
          context.updateTooltips();
        },
        function(error) {
          console.error(error);
          context.isLoaded.logs = true;
          context.updateTooltips();
        },
        true
      );
    },
    validateSearchIp(hideLoader) {
      if (!hideLoader) {
        this.isLoaded.search = false;
      }
      this.error.ipSearch = false;
      this.ipSearch = this.ipSearch.trim();

      var validateObj = {
        action: "search",
        ipAddress: this.ipSearch
      };

      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/analysis/validate"],
        validateObj,
        null,
        function(success) {
          context.searchIp(validateObj);
        },
        function(error, data) {
          context.validationError(error, data);
        }
      );
    },
    validateSearchDomain(hideLoader) {
      if (!hideLoader) {
        this.isLoaded.search = false;
      }
      this.error.domainSearch = false;
      this.domainSearch = this.domainSearch.trim();

      var validateObj = {
        action: "search",
        domain: this.domainSearch
      };

      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/analysis/validate"],
        validateObj,
        null,
        function(success) {
          context.searchDomain(validateObj);
        },
        function(error, data) {
          context.validationError(error, data);
        }
      );
    },
    validateSearchIpOrDomain() {
      this.error.ipOrDomainSearch = false;
      this.isLoaded.search = false;
      this.ipOrDomainSearch = this.ipOrDomainSearch.trim();

      var validateObj = {
        action: "search",
        ipOrDomain: this.ipOrDomainSearch
      };

      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/analysis/validate"],
        validateObj,
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          const ipOrDomain = success.ipOrDomain;

          if (ipOrDomain === "ip") {
            context.searchIp({
              action: "search",
              ipAddress: validateObj.ipOrDomain
            });
          } else if (ipOrDomain === "domain") {
            context.searchDomain({
              action: "search",
              domain: validateObj.ipOrDomain
            });
          } else {
            console.error("Invalid ipOrDomain result: " + ipOrDomain);
          }
        },
        function(error, data) {
          context.validationError(error, data);
        }
      );
    },
    validationError(error, data) {
      this.isLoaded.search = true;
      const errorData = JSON.parse(data);

      for (const e in errorData.attributes) {
        const attr = errorData.attributes[e];
        const param = attr.parameter;

        if (param === "ipAddress") {
          this.error.ipSearch = attr.error;
          this.$refs.ipSearch.focus();
        } else if (param === "domain") {
          this.error.domainSearch = attr.error;
          this.$refs.domainSearch.focus();
        } else if (param === "ipOrDomain") {
          this.error.ipOrDomainSearch = attr.error;
          this.$refs.ipOrDomainSearch.focus();
        }
      }
    },
    updateTooltips() {
      setTimeout(() => {
        $('[data-toggle="tooltip"]').tooltip();
      }, 300);
    },
    ipAddressClicked(ipAddress) {
      this.ipSearch = ipAddress;
      this.validateSearchIp(true);
    },
    domainClicked(domain) {
      this.domainSearch = domain;
      this.validateSearchDomain(true);
    },
    searchIp(validateObj) {
      var context = this;
      context.isLoaded.searchModal = false;
      $("#search-result-modal").modal("show");
      nethserver.exec(
        ["nethserver-blacklist/analysis/read"],
        validateObj,
        null,
        function(success) {
          success = JSON.parse(success);
          context.searchResult = success.searchResult;
          context.isLoaded.search = true;
          context.isLoaded.searchModal = true;
        },
        function(error, data) {
          console.error(error);
          context.isLoaded.search = true;
        }
      );
    },
    searchDomain(validateObj) {
      var context = this;
      context.isLoaded.searchModal = false;
      $("#search-result-modal").modal("show");
      nethserver.exec(
        ["nethserver-blacklist/analysis/read"],
        validateObj,
        null,
        function(success) {
          success = JSON.parse(success);
          context.searchResult = success.searchResult;
          $("#search-result-modal").modal("show");
          context.isLoaded.search = true;
          context.isLoaded.searchModal = true;
        },
        function(error, data) {
          console.error(error);
          context.isLoaded.search = true;
        }
      );
    },
    getIpConfig() {
      const context = this;
      context.isLoaded.config = false;
      nethserver.exec(
        ["nethserver-blacklist/ipsets/read"],
        {
          action: "configuration"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          const props = success.configuration.props;

          if (props.status === "enabled") {
            context.ipConfig.status = true;
          } else {
            context.ipConfig.status = false;
          }
          context.getDnsConfig();
        },
        function(error) {
          console.error(error);
          context.isLoaded.config = true;
        }
      );
    },
    getDnsConfig() {
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/dnss/read"],
        {
          action: "configuration"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          const props = success.configuration.props;

          if (props.status === "enabled") {
            context.dnsConfig.status = true;
          } else {
            context.dnsConfig.status = false;
          }

          if (!context.ipConfig.status && context.dnsConfig.status) {
            context.logsType = "dns";
          } else {
            context.logsType = "ip";
          }
          context.isLoaded.config = true;
          context.getLogs();
        },
        function(error) {
          console.error(error);
          context.isLoaded.config = true;
        }
      );
    },
    clearFilter() {
      this.searchFilter = "";
      this.getLogs();
    }
  }
};
</script>

<style scoped>
.search-result {
  display: inline-block;
  padding-top: 3px;
}

.clients-list {
  max-height: 9rem;
  overflow-y: auto;
}

.search-filter-btn {
  padding-left: 0;
}
</style>
