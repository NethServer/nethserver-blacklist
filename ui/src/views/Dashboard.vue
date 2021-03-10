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
    <h2>{{$t('dashboard.title')}}</h2>
    <!-- status -->
    <h3>{{$t('status')}}</h3>
    <div
      v-if="!(isLoaded.ipConfig && isLoaded.dnsConfig)"
      class="spinner form-spinner-loader mg-left-sm"
    ></div>
    <div v-else class="row">
      <div class="stats-container col-xs-12 col-sm-4 col-md-3">
        <span
          :class="['card-pf-utilization-card-details-count stats-count', ipConfig.status ? 'pficon pficon-ok' : 'pficon-off']"
          data-toggle="tooltip"
          data-placement="top"
          :title="$t(ipConfig.status? 'enabled' : 'disabled')"
        ></span>
        <span class="card-pf-utilization-card-details-description stats-description">
          <span class="card-pf-utilization-card-details-line-2 stats-text">
            <span v-if="ipConfig.status">{{ $t('dashboard.ip_blacklist_enabled') }}</span>
            <span v-else>{{ $t('dashboard.ip_blacklist_disabled') }}</span>
          </span>
        </span>
      </div>
      <div class="stats-container col-xs-12 col-sm-4 col-md-3">
        <span
          :class="['card-pf-utilization-card-details-count stats-count', dnsConfig.status ? 'pficon pficon-ok' : 'pficon-off']"
          data-toggle="tooltip"
          data-placement="top"
          :title="$t(dnsConfig.status? 'enabled' : 'disabled')"
        ></span>
        <span class="card-pf-utilization-card-details-description stats-description">
          <span class="card-pf-utilization-card-details-line-2 stats-text">
            <span v-if="dnsConfig.status">{{ $t('dashboard.dns_blacklist_enabled') }}</span>
            <span v-else>{{ $t('dashboard.dns_blacklist_disabled') }}</span>
          </span>
        </span>
      </div>
    </div>
    <!-- last updated -->
    <h3>{{$t('dashboard.last_blacklist_definitions')}}</h3>
    <div
      v-if="!(isLoaded.lastUpdatedIp && isLoaded.lastUpdatedDns)"
      class="spinner form-spinner-loader mg-left-sm"
    ></div>
    <div v-else class="row">
      <div class="col-xs-12 col-sm-4 col-md-3">
        <h4>{{$t('dashboard.ip_blacklist')}}</h4>
        <p v-if="lastUpdatedIp">{{ lastUpdatedIpWords }} ({{ lastUpdatedIp | dateFormat }})</p>
        <p v-else>-</p>
        <button
          type="button"
          class="btn btn-default"
          :disabled="!isLoaded.updateIp || !ipConfig.url || !ipConfig.status"
          @click="updateIpBlacklist()"
        >{{ $t('dashboard.check_for_updates') }}</button>
        <div v-if="!isLoaded.updateIp" class="spinner form-spinner-loader mg-left-md"></div>
      </div>
      <div class="col-xs-12 col-sm-4 col-md-3">
        <h4>{{$t('dashboard.dns_blacklist')}}</h4>
        <p v-if="lastUpdatedDns">{{ lastUpdatedDnsWords }} ({{ lastUpdatedDns | dateFormat }})</p>
        <p v-else>-</p>
        <button
          type="button"
          class="btn btn-default"
          :disabled="!isLoaded.updateDns || !dnsConfig.url || !dnsConfig.status"
          @click="updateDnsBlacklist()"
        >{{ $t('dashboard.check_for_updates') }}</button>
        <div v-if="!isLoaded.updateDns" class="spinner form-spinner-loader mg-left-md"></div>
      </div>
    </div>

    <!-- IP statistics -->
    <h3>{{$t('dashboard.ip_statistics')}}</h3>
    <div v-if="!isLoaded.ipStats" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-if="isLoaded.ipStats">
      <div>
        <div class="stats-container card-pf-utilization-details">
          <span class="card-pf-utilization-card-details-count" :title="ipStats.totalHits">
            {{ ipStats.totalHits | humanFormat }}
          </span>
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
        <div class="col-xs-12 col-md-6 mg-top-md">
          <div v-show="ipStats.mostBlockedSrcHosts.length == 0">
            <div class="blank-slate-pf pie-chart-blank-slate">
              <div class="blank-slate-pf-icon">
                <span class="fa fa-pie-chart"></span>
              </div>
              <h5 class="chart-title gray">{{ $t('dashboard.no_data') }}</h5>
            </div>
          </div>
          <div v-show="ipStats.mostBlockedSrcHosts.length > 0" id="pie-chart-host-src"></div>
          <h5 class="chart-title">{{ $t('dashboard.today_most_blocked_source_hosts') }}</h5>
        </div>
        <!-- most blocked source hosts -->
        <div class="col-xs-12 col-md-6 mg-top-md">
          <div v-show="ipStats.mostBlockedDstHosts.length == 0">
            <div class="blank-slate-pf pie-chart-blank-slate">
              <div class="blank-slate-pf-icon">
                <span class="fa fa-pie-chart"></span>
              </div>
              <h5 class="chart-title gray">{{ $t('dashboard.no_data') }}</h5>
            </div>
          </div>
          <div v-show="ipStats.mostBlockedDstHosts.length > 0" id="pie-chart-host-dst"></div>
          <h5 class="chart-title">{{ $t('dashboard.today_most_blocked_destination_hosts') }}</h5>
        </div>
      </div>
    </div>

    <!-- DNS statistics -->
    <h3>{{$t('dashboard.dns_statistics')}}</h3>

    <div v-if="!isLoaded.dnsStats" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-else>
      <div class="row no-margin">
        <!-- threats blocked today -->
        <div class="stats-container col-xs-12 col-sm-4 col-md-3">
          <span
            class="card-pf-utilization-card-details-count stats-count"
            :title="(dnsStats.general.ads_blocked_today || dnsStats.general.ads_blocked_today == 0) ? dnsStats.general.ads_blocked_today : ''"
          >{{ (dnsStats.general.ads_blocked_today || dnsStats.general.ads_blocked_today == 0) ? dnsStats.general.ads_blocked_today : '-' | humanFormat }}</span>
          <span class="card-pf-utilization-card-details-description stats-description">
            <span
              class="card-pf-utilization-card-details-line-2 stats-text"
            >{{ $t('dashboard.today_total_threats_blocked') }}</span>
          </span>
        </div>
        <!-- dns queries today -->
        <div class="stats-container col-xs-12 col-sm-4 col-md-3">
          <span
            class="card-pf-utilization-card-details-count stats-count"
            :title="(dnsStats.general.dns_queries_today || dnsStats.general.dns_queries_today == 0) ? dnsStats.general.dns_queries_today : ''"
          >{{ (dnsStats.general.dns_queries_today || dnsStats.general.dns_queries_today == 0) ? dnsStats.general.dns_queries_today : '-' | humanFormat}}</span>
          <span class="card-pf-utilization-card-details-description stats-description">
            <span
              class="card-pf-utilization-card-details-line-2 stats-text"
            >{{ $t('dashboard.today_dns_queries') }}</span>
          </span>
        </div>
        <!-- threats percentage today -->
        <div class="stats-container col-xs-12 col-sm-4 col-md-3">
          <span
            class="card-pf-utilization-card-details-count stats-count"
          >{{ dnsStats.general.ads_percentage_today | decimalsFormat }}%</span>
          <span class="card-pf-utilization-card-details-description stats-description">
            <span
              class="card-pf-utilization-card-details-line-2 stats-text"
            >{{ $t('dashboard.today_threats_percentage') }}</span>
          </span>
        </div>
      </div>
      <!-- pie charts -->
      <div class="row">
        <!-- top clients -->
        <div class="col-xs-12 col-md-6 col-lg-4 mg-top-md">
          <div v-show="dnsStats.topClients.length == 0">
            <div class="blank-slate-pf pie-chart-blank-slate">
              <div class="blank-slate-pf-icon">
                <span class="fa fa-pie-chart"></span>
              </div>
              <h5 class="chart-title gray">{{ $t('dashboard.no_data') }}</h5>
            </div>
          </div>
          <div v-show="dnsStats.topClients.length > 0" id="pie-chart-dns-clients"></div>
          <h5 class="chart-title">{{ $t('dashboard.top_clients') }}</h5>
        </div>
        <!-- top blocked domains -->
        <div class="col-xs-12 col-md-6 col-lg-4 mg-top-md">
          <div v-show="dnsStats.topAds.length == 0">
            <div class="blank-slate-pf pie-chart-blank-slate">
              <div class="blank-slate-pf-icon">
                <span class="fa fa-pie-chart"></span>
              </div>
              <h5 class="chart-title gray">{{ $t('dashboard.no_data') }}</h5>
            </div>
          </div>
          <div v-show="dnsStats.topAds.length > 0" id="pie-chart-dns-blocked-domains"></div>
          <h5 class="chart-title">{{ $t('dashboard.top_blocked_domains') }}</h5>
        </div>
        <!-- top requested domains -->
        <div class="col-xs-12 col-md-6 col-lg-4 mg-top-md">
          <div v-show="dnsStats.topDomains.length == 0">
            <div class="blank-slate-pf pie-chart-blank-slate">
              <div class="blank-slate-pf-icon">
                <span class="fa fa-pie-chart"></span>
              </div>
              <h5 class="chart-title gray">{{ $t('dashboard.no_data') }}</h5>
            </div>
          </div>
          <div v-show="dnsStats.topDomains.length > 0" id="pie-chart-dns-domains"></div>
          <h5 class="chart-title">{{ $t('dashboard.top_domains') }}</h5>
        </div>
      </div>
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
      isLoaded: {
        lastUpdatedIp: false,
        lastUpdatedDns: false,
        ipStats: false,
        dnsStats: false,
        ipConfig: false,
        dnsConfig: false,
        updateIp: true,
        updateDns: true
      },
      ipConfig: {
        status: false,
        url: null
      },
      dnsConfig: {
        status: false,
        url: null
      },
      lastUpdatedIp: null,
      lastUpdatedDns: null,
      ipStats: {},
      dnsStats: {}
    };
  },
  methods: {
    getDashboardData() {
      this.getIpConfig();
      this.getDnsConfig();
      this.getLastUpdatedIp();
      this.getLastUpdatedDns();
      this.getIpStats();
      this.getDnsStats();
    },
    getLastUpdatedIp() {
      const context = this;
      context.isLoaded.lastUpdatedIp = false;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/read"],
        {
          action: "last-updated",
          type: "ipsets"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          const millis = success.lastUpdated * 1000;
          context.lastUpdatedIp = millis;
          context.lastUpdatedIpWords = moment
            .unix(success.lastUpdated)
            .fromNow();
          context.isLoaded.lastUpdatedIp = true;
        },
        function(error) {
          console.error(error);
          context.isLoaded.lastUpdatedIp = true;
        }
      );
    },
    getLastUpdatedDns() {
      const context = this;
      context.isLoaded.lastUpdatedDns = false;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/read"],
        {
          action: "last-updated",
          type: "dnss"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          const millis = success.lastUpdated * 1000;
          context.lastUpdatedDns = millis;
          context.lastUpdatedDnsWords = moment
            .unix(success.lastUpdated)
            .fromNow();
          context.isLoaded.lastUpdatedDns = true;
        },
        function(error) {
          console.error(error);
          context.isLoaded.lastUpdatedDns = true;
        }
      );
    },
    getIpStats() {
      this.isLoaded.ipStats = false;
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/read"],
        {
          action: "statistics",
          type: "ipsets",
          limit: 10
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            context.ipStats = success.statistics;
            context.shortenChartLegend(context.ipStats.mostBlockedSrcHosts);
            context.shortenChartLegend(context.ipStats.mostBlockedDstHosts);
            context.isLoaded.ipStats = true;

            setTimeout(function() {
              context.initStatsChart("host-src");
              context.initStatsChart("host-dst");
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
    shortenChartLegend(chartData) {
      // shorten chart label if it exceeds character length
      const MAX_LENGTH = 20;

      for (let chartEntry of chartData) {
        if (chartEntry[0].length > MAX_LENGTH) {
          chartEntry[0] = chartEntry[0].substring(0, MAX_LENGTH) + "...";
        }
      }
    },
    getDnsStats() {
      this.isLoaded.dnsStats = false;
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/dashboard/read"],
        {
          action: "statistics",
          type: "dnss",
          limit: 10
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          context.dnsStats = success.statistics;
          context.shortenChartLegend(context.dnsStats.topClients);
          context.shortenChartLegend(context.dnsStats.topAds);
          context.shortenChartLegend(context.dnsStats.topDomains);
          context.isLoaded.dnsStats = true;

          setTimeout(function() {
            context.initStatsChart("dns-clients");
            context.initStatsChart("dns-blocked-domains");
            context.initStatsChart("dns-domains");
          }, 250);
        },
        function(error) {
          console.error(error);
          context.isLoaded.dnsStats = true;
        }
      );
    },
    initStatsChart(type) {
      var c3ChartDefaults = $().c3ChartDefaults();

      var columnsData;

      switch (type) {
        case "host-src":
          columnsData = this.ipStats.mostBlockedSrcHosts;
          break;
        case "host-dst":
          columnsData = this.ipStats.mostBlockedDstHosts;
          break;
        case "dns-clients":
          columnsData = this.dnsStats.topClients;
          break;
        case "dns-blocked-domains":
          columnsData = this.dnsStats.topAds;
          break;
        case "dns-domains":
          columnsData = this.dnsStats.topDomains;
          break;
      }

      var pieData = {
        type: "pie",
        columns: columnsData
      };

      var pieChartConfig = c3ChartDefaults.getDefaultPieConfig();
      pieChartConfig.bindto = "#pie-chart-" + type;
      pieChartConfig.data = pieData;
      pieChartConfig.legend = {
        show: true,
        position: "right"
      };
      pieChartConfig.size = {
        width: 350,
        height: 250
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
    updateIpBlacklist() {
      this.isLoaded.updateIp = false;
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
          action: "update",
          type: "ipsets"
        },
        function(stream) {
          console.info("blacklist-ip-download", stream);
        },
        function(success) {
          context.isLoaded.updateIp = true;
          context.getDashboardData();
        },
        function(error, data) {
          console.error(error);
          context.isLoaded.updateIp = true;
        }
      );
    },
    updateDnsBlacklist() {
      this.isLoaded.updateDns = false;
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
          action: "update",
          type: "dnss"
        },
        function(stream) {
          console.info("blacklist-dns-download", stream);
        },
        function(success) {
          context.isLoaded.updateDns = true;
          context.getDashboardData();
        },
        function(error, data) {
          console.error(error);
          context.isLoaded.updateDns = true;
        }
      );
    },
    getIpConfig() {
      const context = this;
      context.isLoaded.ipConfig = false;
      nethserver.exec(
        ["nethserver-blacklist/ipsets/read"],
        {
          action: "configuration"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            const props = success.configuration.props;
            context.ipConfig.url = props.Url;

            if (props.status === "enabled") {
              context.ipConfig.status = true;
            } else {
              context.ipConfig.status = false;
            }
            context.isLoaded.ipConfig = true;
          } catch (e) {
            console.error(e);
          }
        },
        function(error) {
          console.error(error);
        }
      );
    },
    getDnsConfig() {
      const context = this;
      context.isLoaded.dnsConfig = false;
      nethserver.exec(
        ["nethserver-blacklist/dnss/read"],
        {
          action: "configuration"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            const props = success.configuration.props;
            context.dnsConfig.url = props.Url;

            if (props.status === "enabled") {
              context.dnsConfig.status = true;
            } else {
              context.dnsConfig.status = false;
            }
            context.isLoaded.dnsConfig = true;
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

.pie-chart-blank-slate {
  height: 250px; /* same height as pie-chart */
  margin-bottom: 0;
  padding: 30px;
}
</style>
