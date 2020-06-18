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
    <!-- IP search -->
    <h3>{{$t('analysis.ip_search_title')}}</h3>
    <form class="form-horizontal" v-on:submit.prevent="validateSearchIp()">
      <div :class="['form-group', {'has-error': error.ipSearch}]">
        <label class="col-sm-2 control-label" for="ip-search">
          {{$t('analysis.ip_address')}}
          <doc-info :placement="'bottom'" :chapter="'search_ip_address'" :inline="true"></doc-info>
        </label>
        <div class="col-sm-3">
          <input type="text" v-model="ipSearch" id="ip-search" ref="ipSearch" class="form-control" />
          <span
            v-if="error.ipSearch"
            class="help-block"
          >{{$t('validation.ip_search_' + error.ipSearch)}}</span>
        </div>
      </div>
      <!-- check button -->
      <div class="form-group">
        <label class="col-sm-2 control-label label-loader">
          <div
            v-if="!isLoaded.search"
            class="spinner spinner-sm form-spinner-loader adjust-top-loader"
          ></div>
        </label>
        <span class="col-sm-2">
          <button
            class="btn btn-default"
            type="submit"
            :disabled="!isLoaded.search || !isLoaded.categories"
          >{{$t('analysis.check')}}</button>
        </span>
      </div>
    </form>
    <div v-if="showIpSearchResult" class="alert alert-info alert-dismissable">
      <span class="pficon pficon-info"></span>
      {{$t('analysis.ip_address')}}
      <b>{{ ipSearchCompleted }}</b>
      <span v-if="ipSearchResult">
        {{ $t('analysis.ip_blocked_from_category') }}
        <b>{{ ipSearchResult }}</b>
      </span>
      <span v-if="!ipSearchResult">&nbsp;{{ $t('analysis.ip_not_blocked') }}</span>
    </div>
    <h3>{{$t('analysis.logs')}}</h3>
    <form class="form-horizontal" v-on:submit.prevent="getLogs()">
      <!-- filter -->
      <div class="form-group">
        <label class="col-sm-2 control-label" for="searchFilter">{{$t('analysis.filter')}}</label>
        <div class="col-sm-3">
          <input type="text" v-model="searchFilter" id="searchFilter" class="form-control" />
        </div>
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
            max="10000"
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
            class="btn btn-default"
            type="submit"
            :disabled="!isLoaded.logs"
          >{{$t('analysis.search_logs')}}</button>
        </span>
      </div>
    </form>
    <div v-show="!isLoaded.logs" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-show="isLoaded.logs">
      <div class="col-sm-12">
        <vue-good-table
          :columns="columns"
          :rows="logs"
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
              <span>{{props.row.interface}}</span>
            </span>
            <span v-if="props.column.field == 'source'">
              <span
                data-toggle="tooltip"
                data-placement="top"
                :title="$t('analysis.ip_search_title')"
              >
                <a @click="ipAddressClicked(props.row.source)">{{props.row.source}}</a>
              </span>
            </span>
            <span v-if="props.column.field == 'dest'">
              <span
                data-toggle="tooltip"
                data-placement="top"
                :title="$t('analysis.ip_search_title')"
              >
                <a @click="ipAddressClicked(props.row.dest)">{{props.row.dest}}</a>
              </span>
            </span>
            <span v-if="props.column.field == 'protocol'">
              <span>{{props.row.protocol}}</span>
            </span>
            <span v-if="props.column.field == 'dest_port'">
              <span>{{props.row.dest_port}}</span>
            </span>
            <span v-if="props.column.field == 'dest_service'">
              <span>{{props.row.dest_service ? props.row.dest_service : '-'}}</span>
            </span>
          </template>
        </vue-good-table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Analysis",
  mounted() {
    this.getCategories();
    this.getLogs();
  },
  data() {
    return {
      searchFilter: "",
      logs: [],
      lines: 500,
      isLoaded: {
        search: true,
        categories: false,
        logs: false
      },
      tableLangsTexts: this.tableLangs(),
      columns: [
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
      error: {
        ipSearch: false
      },
      ipSearch: "",
      ipSearchCompleted: "",
      ipSearchResult: "",
      showIpSearchResult: false,
      allCategories: []
    };
  },
  methods: {
    getLogs() {
      this.isLoaded.logs = false;
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/analysis/read"],
        {
          action: "logs",
          filter: this.searchFilter,
          lines: this.lines
        },
        null,
        function(success) {
          success = JSON.parse(success);
          context.logs = success.logs;
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
    validateSearchIp() {
      this.error.ipSearch = false;
      this.isLoaded.search = false;
      this.showIpSearchResult = false;
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
    validationError(error, data) {
      this.isLoaded.search = true;
      const errorData = JSON.parse(data);

      for (const e in errorData.attributes) {
        const attr = errorData.attributes[e];
        const param = attr.parameter;

        if (param === "ipAddress") {
          this.error.ipSearch = attr.error;
          this.$refs.ipSearch.focus();
        }
      }
    },
    updateTooltips() {
      setTimeout(() => {
        $('[data-toggle="tooltip"]').tooltip();
      }, 300);
    },
    ipAddressClicked(ipAddress) {
      window.scrollTo(0,0);
      this.ipSearch = ipAddress;
      this.validateSearchIp();
    },
    searchIp(validateObj) {
      var context = this;
      nethserver.exec(
        ["nethserver-blacklist/analysis/read"],
        validateObj,
        null,
        function(success) {
          success = JSON.parse(success);
          context.isLoaded.search = true;
          context.ipSearchResult = success.searchResult;
          context.ipSearchCompleted = context.ipSearch;

          if (context.ipSearchResult) {
            // retrieve category name
            var categoryFound = context.allCategories.find(category => {
              return category.id === context.ipSearchResult;
            });

            if (categoryFound) {
              context.ipSearchResult = categoryFound.name;
            }
          }
          context.showIpSearchResult = true;
        },
        function(error, data) {
          console.error(error);
          context.isLoaded.search = true;
        }
      );
    },
    getCategories() {
      const context = this;
      context.isLoaded.categories = false;
      nethserver.exec(
        ["nethserver-blacklist/ipsets/read"],
        {
          action: "categories"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            context.allCategories = success.categories;
            context.isLoaded.categories = true;
          } catch (e) {
            console.error(e);
          }
        },
        function(error) {
          console.error(error);
        }
      );
    }
  }
};
</script>

<style scoped>
</style>
