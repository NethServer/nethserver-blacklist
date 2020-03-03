<template>
  <div>
    <h2>{{$t('dashboard.title')}}</h2>
    <!-- error message -->
    <div v-if="errorMessage" class="alert alert-danger alert-dismissable">
      <button type="button" class="close" @click="closeErrorMessage()" aria-label="Close">
        <span class="pficon pficon-close"></span>
      </button>
      <span class="pficon pficon-error-circle-o"></span>
      {{ errorMessage }}.
    </div>
    <!-- status -->
    <h3>{{$t('status')}}</h3>
    <div v-if="!isLoaded.config" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-if="isLoaded.config" class="row">
      <div class="stats-container col-xs-12 col-sm-4 col-md-3 col-lg-2">
        <span
          :class="['card-pf-utilization-card-details-count stats-count', config.status ? 'pficon pficon-ok' : 'pficon-off']"
          data-toggle="tooltip"
          data-placement="top"
          :title="$t(config.status? 'enabled' : 'disabled')"
        ></span>
        <span class="card-pf-utilization-card-details-description stats-description">
          <span class="card-pf-utilization-card-details-line-2 stats-text">
            <span v-if="config.status">{{ $t('dashboard.blacklist_enabled') }}</span>
            <span v-else>{{ $t('dashboard.blacklist_disabled') }}</span>
          </span>
        </span>
      </div>
    </div>
    <!-- last updated -->
    <h3>{{$t('dashboard.last_blacklist_definitions')}}</h3>
    <div v-if="!isLoaded.lastUpdated" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-if="isLoaded.lastUpdated">
      <p v-if="lastUpdated">{{ lastUpdatedWords }} ({{ lastUpdated | dateFormat }})</p>
      <p v-else>-</p>
      <button
        type="button"
        class="btn btn-default"
        :disabled="!isLoaded.update"
        @click="updateBlacklist()"
      >{{ $t('dashboard.check_for_updates') }}</button>
      <div v-if="!isLoaded.update" class="spinner form-spinner-loader mg-left-md"></div>
    </div>

    <!-- statistics -->
    <h3>{{$t('dashboard.statistics')}}</h3>
    <div v-if="!isLoaded.stats" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-if="isLoaded.stats">
      <div>
        <div class="stats-container card-pf-utilization-details">
          <span class="card-pf-utilization-card-details-count">{{ stats.totalHits }}</span>
          <span class="card-pf-utilization-card-details-description">
            <span
              class="card-pf-utilization-card-details-line-2 stats-text"
            >{{ $t('dashboard.today_total_threats_blocked') }}</span>
          </span>
        </div>
      </div>
      <!-- pie charts -->
      <div class="row">
        <!-- most blocked source hosts -->
        <div class="col-md-6 mg-top-md">
          <div v-show="stats.mostBlockedSrcHosts.length == 0">
            <div class="blank-slate-pf padding-30">
              <div class="blank-slate-pf-icon">
                <span class="fa fa-pie-chart"></span>
              </div>
              <h4 class="chart-title gray">{{ $t('dashboard.no_data') }}</h4>
            </div>
          </div>
          <div v-show="stats.mostBlockedSrcHosts.length > 0" id="pie-chart-host-src"></div>
          <h4 class="chart-title">{{ $t('dashboard.today_most_blocked_source_hosts') }}</h4>
        </div>
        <!-- most blocked source hosts -->
        <div class="col-md-6 mg-top-md">
          <div v-show="stats.mostBlockedDstHosts.length == 0">
            <div class="blank-slate-pf padding-30">
              <div class="blank-slate-pf-icon">
                <span class="fa fa-pie-chart"></span>
              </div>
              <h4 class="chart-title gray">{{ $t('dashboard.no_data') }}</h4>
            </div>
          </div>
          <div v-show="stats.mostBlockedDstHosts.length > 0" id="pie-chart-host-dst"></div>
          <h4 class="chart-title">{{ $t('dashboard.today_most_blocked_destination_hosts') }}</h4>
        </div>
      </div>
    </div>
    <!-- IP search -->
    <h3>{{$t('dashboard.ip_search_title')}}</h3>
    <form class="form-horizontal" v-on:submit.prevent="validateSearchIp()">
      <div :class="['form-group', {'has-error': error.ipSearch}]">
        <label class="col-sm-2 control-label" for="ip-search">{{$t('dashboard.ip_address')}}</label>
        <div class="col-sm-3">
          <input type="text" v-model="ipSearch" id="ip-search" ref="ipSearch" class="form-control" />
          <span
            v-if="error.ipSearch"
            class="help-block"
          >{{$t('validation.ip_search_' + error.ipSearch)}}</span>
        </div>
      </div>
      <!-- search button -->
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
            :disabled="!isLoaded.search || !isLoaded.categories"
          >{{$t('search')}}</button>
        </span>
      </div>
    </form>
    <div v-if="showIpSearchResult" class="alert alert-info alert-dismissable">
      <span class="pficon pficon-info"></span>
      {{$t('dashboard.ip_address')}}
      <b>{{ ipSearchCompleted }}</b>
      <span v-if="ipSearchResult">
        {{ $t('dashboard.ip_blocked_from_category') }}
        <b>{{ ipSearchResult }}</b>
      </span>
      <span v-if="!ipSearchResult">&nbsp;{{ $t('dashboard.ip_not_blocked') }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "Dashboard",
  props: {},
  mounted() {
    this.getDashboardData();
  },
  data() {
    return {
      errorMessage: null,
      isLoaded: {
        lastUpdated: false,
        stats: false,
        categories: false,
        config: false,
        update: true,
        search: true
      },
      config: {
        status: false
      },
      lastUpdated: null,
      stats: {},
      error: {
        ipSearch: false
      },
      ipSearch: "",
      ipSearchCompleted: "",
      ipSearchResult: "",
      showIpSearchResult: false,
      error: {
        ipSearch: false
      }
    };
  },
  methods: {
    showErrorMessage(errorMessage, error) {
      console.error(errorMessage, error);
      this.errorMessage = errorMessage;
    },
    closeErrorMessage() {
      this.errorMessage = null;
    },
    getDashboardData() {
      this.getConfig();
      this.getLastUpdated();
      this.getStats();
      this.getCategories();
    },
    getCategories() {
      const context = this;
      context.isLoaded.categories = false;
      nethserver.exec(
        ["nethserver-blacklist/settings/read"],
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
    },
    getLastUpdated() {
      const context = this;
      context.isLoaded.lastUpdated = false;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/read"],
        {
          action: "last-updated"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            const millis = success.lastUpdated * 1000;
            context.lastUpdated = millis;
            context.lastUpdatedWords = moment
              .unix(success.lastUpdated)
              .fromNow();
            context.isLoaded.lastUpdated = true;
          } catch (e) {
            console.error(e);
          }
        },
        function(error) {
          console.error(error);
        }
      );
    },
    getStats() {
      this.isLoaded.stats = false;
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/read"],
        {
          action: "statistics"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            context.stats = success.statistics;
            context.isLoaded.stats = true;

            setTimeout(function() {
              context.initStatsChart("src");
              context.initStatsChart("dst");
            }, 250);
          } catch (e) {
            console.error(e);
          }
        },
        function(error) {
          console.error(error);
        }
      );
    },
    initStatsChart(type) {
      var c3ChartDefaults = $().c3ChartDefaults();

      var pieData = {
        type: "pie",
        columns:
          type === "src"
            ? this.stats.mostBlockedSrcHosts
            : this.stats.mostBlockedDstHosts
      };

      var pieChartConfig = c3ChartDefaults.getDefaultPieConfig();
      pieChartConfig.bindto = "#pie-chart-host-" + type;
      pieChartConfig.data = pieData;
      pieChartConfig.legend = {
        show: true,
        position: "right"
      };
      pieChartConfig.size = {
        width: 450,
        height: 220
      };
      pieChartConfig.color = {
        pattern: [
          $.pfPaletteColors.orange,
          $.pfPaletteColors.red,
          $.pfPaletteColors.blue,
          $.pfPaletteColors.green,
          $.pfPaletteColors.gold,
          $.pfPaletteColors.purple,
          $.pfPaletteColors.black
        ]
      };
      var pieChartLegend = c3.generate(pieChartConfig);
    },
    updateBlacklist() {
      this.isLoaded.update = false;
      nethserver.notifications.success = this.$i18n.t(
        "dashboard.blacklist_update_successful"
      );
      nethserver.notifications.error = this.$i18n.t(
        "dashboard.blacklist_update_failed"
      );
      var context = this;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/execute"],
        {
          action: "update"
        },
        function(stream) {
          console.info("blacklist-download", stream);
        },
        function(success) {
          context.isLoaded.update = true;
          context.getDashboardData();
        },
        function(error, data) {
          console.error(error);
          context.isLoaded.update = true;
        }
      );
    },
    validateSearchIp() {
      this.error.ipSearch = false;
      this.isLoaded.search = false;
      this.showIpSearchResult = false;

      var validateObj = {
        action: "search",
        ipAddress: this.ipSearch
      };

      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/validate"],
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
    searchIp(validateObj) {
      var context = this;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/read"],
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
    getConfig() {
      const context = this;
      context.isLoaded.config = false;
      nethserver.exec(
        ["nethserver-blacklist/settings/read"],
        {
          action: "configuration"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            const props = success.configuration.props;

            if (props.status === "enabled") {
              context.config.status = true;
            } else {
              context.config.status = false;
            }
            context.isLoaded.config = true;
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
.chart-title {
  text-align: center;
}
</style>
