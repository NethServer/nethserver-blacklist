<template>
  <div>
    <h2>{{$t('settings.title')}}</h2>
    <!-- error message -->
    <div v-if="errorMessage" class="alert alert-danger alert-dismissable">
      <button type="button" class="close" @click="closeErrorMessage()" aria-label="Close">
        <span class="pficon pficon-close"></span>
      </button>
      <span class="pficon pficon-error-circle-o"></span>
      {{ errorMessage }}.
    </div>
    <div v-if="!isLoaded.config" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-if="isLoaded.config">
      <form class="form-horizontal" v-on:submit.prevent="saveSettings(true)">
        <!-- status -->
        <div class="form-group">
          <label class="col-sm-2 control-label" for="blacklist-status">{{$t('enabled')}}</label>
          <div class="col-sm-2">
            <input
              type="checkbox"
              v-model="config.status"
              id="blacklist-status"
              class="form-control"
            />
          </div>
        </div>
        <!-- download url -->
        <div :class="['form-group', {'has-error': error.url}]">
          <label class="col-sm-2 control-label" for="blacklist-url">
            {{$t('settings.download_url')}}
            <doc-info :placement="'top'" :chapter="'blacklist_download_url'" :inline="true"></doc-info>
          </label>
          <div class="col-sm-5">
            <input
              type="url"
              v-model="config.url"
              id="blacklist-url"
              ref="blacklistUrl"
              class="form-control"
              :disabled="!config.status"
            />
            <span v-if="error.url" class="help-block">{{$t('validation.url_' + error.url)}}</span>
          </div>
        </div>
        <!-- whitelist -->
        <div :class="['form-group', {'has-error': error.whitelist}]">
          <label class="col-sm-2 control-label">{{$t('settings.whitelist')}}</label>
          <div class="col-sm-5">
            <div id="pf-list-standard" class="list-group list-view-pf list-view-pf-view whitelist">
              <div v-for="item in config.whitelist" v-bind:key="item.name" class="list-group-item">
                <div class="list-view-pf-actions whitelist-button-c">
                  <button
                    type="button"
                    class="btn btn-danger btn-xs whitelist-button"
                    :disabled="!config.status"
                    @click="deleteWhitelistItem(item)"
                  >{{ $t('delete') }}</button>
                </div>
                <div class="list-view-pf-main-info pad-top-bottom-sm">
                  <div class="list-view-pf-body">
                    <div class="list-view-pf-description">
                      <div class="list-group-item-text whitelist-elem">
                        <span>
                          {{item.name}}
                          <span
                            v-show="item.IpAddress || item.Address"
                            class="gray"
                          >({{ item.IpAddress || item.Address }})</span>
                          <i class="mg-left-5">{{item.Description}}</i>
                          <b class="mg-left-5">{{item.type | capitalize}}</b>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <!-- new whitelist element -->
              <div class="list-group-item">
                <div class="list-view-pf-actions whitelist-button-c">
                  <button
                    type="button"
                    class="btn btn-default btn-xs whitelist-button"
                    :disabled="!config.status || !newWhitelistElem.name.trim()"
                    @click="addWhitelistItem()"
                  >{{ $t('add') }}</button>
                </div>
                <div class="list-view-pf-main-info pad-top-bottom-sm">
                  <div class="list-view-pf-body">
                    <div class="list-view-pf-description">
                      <div class="list-group-item-text whitelist-elem">
                        <suggestions
                          v-model="newWhitelistElem.name"
                          :options="autoOptions"
                          :onInputChange="filterWhitelistElem"
                          :onItemSelected="selectWhitelistElem"
                          ref="whitelistSuggestions"
                        >
                          <div slot="item" slot-scope="props" class="single-item">
                            <span>
                              {{props.item.name}}
                              <span
                                v-show="props.item.IpAddress || props.item.Address"
                                class="gray"
                              >({{ props.item.IpAddress || props.item.Address }})&nbsp;</span>
                              <i class="mg-left-5">{{props.item.Description}}&nbsp;</i>
                              <b class="mg-left-5">{{props.item.type | capitalize}}</b>
                            </span>
                          </div>
                        </suggestions>
                        <span
                          v-if="newWhitelistElemType && newWhitelistElemType.length > 0"
                          class="help-block gray font-size-normal"
                        >{{ newWhitelistElemType }}</span>
                        <span
                          v-if="error.whitelist"
                          class="help-block font-size-normal"
                        >{{$t('validation.whitelist_' + error.whitelist)}}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- save settings -->
        <div class="form-group">
          <label class="col-sm-2 control-label label-loader">
            <div
              v-if="!isLoaded.save"
              class="spinner spinner-sm form-spinner-loader adjust-top-loader"
            ></div>
          </label>
          <span class="col-sm-2">
            <button class="btn btn-primary" type="submit" :disabled="!isLoaded.save">{{$t('save')}}</button>
          </span>
        </div>
      </form>
    </div>
    <!-- categories -->
    <h3>{{$t('settings.categories')}}</h3>
    <div v-show="!isLoaded.categories" class="spinner form-spinner-loader mg-left-sm"></div>
    <div v-show="isLoaded.categories">
      <div class="col-sm-12">
        <vue-good-table
          :columns="columns"
          :rows="allCategories"
          :lineNumbers="false"
          :sort-options="{
            enabled: true,
            initialSortBy: {field: 'confidence', type: 'desc'}
          }"
          :globalSearch="false"
          :paginate="false"
          styleClass="table condensed"
          :nextText="tableLangsTexts.nextText"
          :prevText="tableLangsTexts.prevText"
          :rowsPerPageText="tableLangsTexts.rowsPerPageText"
          :globalSearchPlaceholder="tableLangsTexts.globalSearchPlaceholder"
          :ofText="tableLangsTexts.ofText"
        >
          class="category-table"
          >
          <template slot="table-row" slot-scope="props">
            <td :class="['fancy', {'gray': !props.row.selected}]">
              <span :title="$t(props.row.selected ? 'enabled' : 'disabled')">
                <span
                  :class="['category-status-icon', 'pficon', props.row.selected ? ['pficon-ok', 'green'] : 'pficon-off']"
                ></span>
              </span>
              <span :title="$t('settings.' + props.row.id + '_description')">
                <span class="semi-bold">{{props.row.name}}</span>
              </span>
            </td>
            <td :class="['fancy', {'gray': !props.row.selected}]">
              <span
                :class="['confidence', props.row.selected ? (parseInt(props.row.confidence) > 6 ? 'green' : 'orange') : 'gray']"
              >{{props.row.confidence}}/10</span>
            </td>
            <td :class="['fancy', {'gray': !props.row.selected}]">{{props.row.type | capitalize}}</td>
            <td :class="['fancy', {'gray': !props.row.selected}]">{{props.row.maintainer}}</td>
            <td :class="['fancy', {'gray': !props.row.selected}]">
              <button
                v-show="props.row.selected"
                @click="toggleCategory(props.row, false)"
                class="btn btn-danger"
                :disabled="!config.status || isLoading.toggleCategory[props.row.id]"
              >{{$t('disable')}}</button>
              <button
                v-show="!props.row.selected"
                @click="toggleCategory(props.row, true)"
                class="btn btn-primary"
                :disabled="!config.status || isLoading.toggleCategory[props.row.id]"
              >{{$t('enable')}}</button>
            </td>
          </template>
        </vue-good-table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Settings",
  mounted() {
    this.getBlacklistData();
  },
  data() {
    return {
      errorMessage: null,
      isLoaded: {
        config: false,
        categories: false,
        save: true
      },
      isLoading: {
        toggleCategory: []
      },
      config: {
        status: false,
        url: "",
        whitelist: [],
        categories: [],
        lastUrl: ""
      },
      firewallUiInstalled: false,
      allCategories: [],
      selectedCategories: [],
      columns: [
        {
          label: this.$i18n.t("settings.name"),
          field: "name",
          sortable: false
        },
        {
          label: this.$i18n.t("settings.confidence"),
          field: "confidence",
          type: "number",
          sortable: true
        },
        {
          label: this.$i18n.t("settings.type"),
          field: "type",
          sortable: true
        },
        {
          label: this.$i18n.t("settings.maintainer"),
          field: "maintainer",
          sortable: true
        },
        {
          label: this.$i18n.t("actions"),
          field: "",
          sortable: false
        }
      ],
      tableLangsTexts: this.tableLangs(),
      error: {
        url: false,
        whitelist: false
      },
      autoOptions: {
        inputClass: ["form-control", "no-border-shadow"],
        placeholder: this.firewallUiInstalled
          ? this.$t("settings.new_whitelist_element_fw")
          : this.$t("settings.new_whitelist_element")
      },
      newWhitelistElem: {
        name: ""
      },
      newWhitelistElemType: "",
      hosts: [],
      cidrSubs: []
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
    getBlacklistData() {
      this.getFirewallUiInstalled();
      this.getConfig();
    },
    getFirewallUiInstalled() {
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/settings/read"],
        {
          action: "firewall-ui-installed"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
            context.firewallUiInstalled = success.firewallUiInstalled;

            if (context.firewallUiInstalled) {
              context.getHosts();
              context.getCIDRSubs();
            }
          } catch (e) {
            console.error(e);
          }
        },
        function(error) {
          console.error(error);
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
            context.config.url = props.Url;
            context.config.lastUrl = context.config.url;
            context.config.whitelist = context.buildWhitelist(props.Whitelist);
            context.config.categories = props.Categories.split(",");
            context.isLoaded.config = true;
            context.getCategories();
          } catch (e) {
            console.error(e);
          }
        },
        function(error) {
          console.error(error);
        }
      );
    },
    buildWhitelist(whitelistString) {
      var whitelistIds = whitelistString.split(",");
      var whitelist = [];

      for (var whitelistId of whitelistIds) {
        if (whitelistId) {
          if (whitelistId.startsWith("host;")) {
            const hostName = whitelistId.replace("host;", "");

            var host = this.hosts.find(host => {
              return host.name === hostName;
            });
            whitelist.push(host);
          } else if (whitelistId.startsWith("cidr;")) {
            const cidrName = whitelistId.replace("cidr;", "");

            var cidr = this.cidrSubs.find(cidr => {
              return cidr.name === cidrName;
            });
            whitelist.push(cidr);
          } else {
            whitelist.push({ name: whitelistId });
          }
        }
      }
      return whitelist;
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
            context.allCategories.forEach(category => {
              category.selected = false;
            });

            for (var selectedCategory of context.config.categories) {
              var categoryFound = context.allCategories.find(category => {
                return category.id === selectedCategory;
              });

              if (categoryFound) {
                categoryFound.selected = true;
              }
            }
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
    getWhitelistIds() {
      // return an array with the correct IDs of whitelist
      var whitelistIds = [];

      for (var elem of this.config.whitelist) {
        if (!elem.typeId) {
          // manually entered
          whitelistIds.push(elem.name);
        } else if (elem.typeId === "host") {
          whitelistIds.push("host;" + elem.name);
        } else if (elem.typeId === "cidr") {
          whitelistIds.push("cidr;" + elem.name);
        }
      }
      return whitelistIds;
    },
    getSelectedCategoriesIds() {
      let categoryIds = [];

      for (let category of this.allCategories) {
        if (category.selected) {
          categoryIds.push(category.id);
        }
      }
      return categoryIds;
    },
    saveSettings(saveButtonLoader) {
      if (saveButtonLoader) {
        this.isLoaded.save = false;
      }
      this.error.url = null;
      this.error.whitelist = null;

      var validateObj = {
        status: this.config.status ? "enabled" : "disabled",
        Url: this.config.url,
        Whitelist: this.getWhitelistIds(),
        Categories: this.getSelectedCategoriesIds()
      };

      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/settings/validate"],
        validateObj,
        null,
        function(success) {
          context.validationSuccess(validateObj);
        },
        function(error, data) {
          context.validationError(error, data);
        }
      );
    },
    validationSuccess(validateObj) {
      nethserver.notifications.success = this.$i18n.t(
        "settings.settings_update_successful"
      );
      nethserver.notifications.error = this.$i18n.t(
        "settings.settings_update_failed"
      );
      validateObj.urlChanged = this.config.lastUrl !== this.config.url;
      const context = this;
      nethserver.exec(
        ["nethserver-blacklist/settings/update"],
        validateObj,
        function(stream) {
          console.info("blacklist-configuration-update", stream);
        },
        function(success) {
          context.isLoaded.save = true;
          context.isLoading.toggleCategory = [];
          context.getBlacklistData();
        },
        function(error) {
          console.error(error);
          context.isLoaded.save = true;
          context.isLoading.toggleCategory = [];
        }
      );
    },
    validationError(error, data) {
      this.isLoaded.save = true;
      this.isLoading.toggleCategory = [];
      const errorData = JSON.parse(data);

      for (const e in errorData.attributes) {
        const attr = errorData.attributes[e];
        const param = attr.parameter;

        if (param === "BlackListUrl") {
          this.error.url = attr.error;
          this.$refs.blacklistUrl.focus();
        } else if (param === "WhiteList") {
          this.error.whitelist = attr.error;
        }
      }
    },
    filterWhitelistElem(query) {
      this.newWhitelistElem = { name: query.trim() };
      this.error.whitelist = null;
      this.newWhitelistElemType = "";

      if (query.trim().length === 0) {
        return null;
      }
      var objects = this.hosts.concat(this.cidrSubs);

      return objects.filter(function(service) {
        return (
          service.typeId.toLowerCase().includes(query.toLowerCase()) ||
          service.name.toLowerCase().includes(query.toLowerCase()) ||
          service.Description.toLowerCase().includes(query.toLowerCase()) ||
          (service.IpAddress &&
            service.IpAddress.toLowerCase().includes(query.toLowerCase()))
        );
      });
    },
    selectWhitelistElem(item) {
      this.error.whitelist = null;

      if (!this.checkWhitelistDuplicated(item.name)) {
        return;
      }

      this.newWhitelistElem = item;
      this.newWhitelistElemType =
        item.name +
        " " +
        (item.IpAddress ? item.IpAddress + " " : "") +
        (item.Address ? item.Address + " " : "") +
        (item.Start && item.End ? item.Start + " - " + item.End + " " : "") +
        "(" +
        item.type +
        ")";
    },
    getHosts() {
      const context = this;

      nethserver.exec(
        ["nethserver-firewall-base/objects/read"],
        {
          action: "hosts"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          context.hosts = success["hosts"];
          context.hosts = context.hosts.map(function(i) {
            i.type = context.$i18n.t("settings.host");
            i.typeId = "host";
            return i;
          });
        },
        function(error) {
          console.error(error);
        }
      );
    },
    getCIDRSubs() {
      const context = this;

      nethserver.exec(
        ["nethserver-firewall-base/objects/read"],
        {
          action: "cidr-subs"
        },
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          context.cidrSubs = success["cidr-subs"];
          context.cidrSubs = context.cidrSubs.map(function(i) {
            i.type = context.$i18n.t("settings.cidr_sub");
            i.typeId = "cidr";
            return i;
          });
          context.getConfig();
        },
        function(error) {
          console.error(error);
        }
      );
    },
    validateNewWhitelistElem(item) {
      this.error.whitelist = null;

      if (!this.checkWhitelistDuplicated(item.name)) {
        return false;
      }

      // check IP address / CIDR syntax if manually entered
      if (!this.newWhitelistElem.typeId && !this.checkIpCidrSyntax(item.name)) {
        return false;
      }
      return true;
    },
    checkIpCidrSyntax(address) {
      const regex = /^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$/;
      if (!regex.test(address)) {
        this.error.whitelist = "invalid";
        return false;
      }
      return true;
    },
    checkWhitelistDuplicated(name) {
      const found = this.config.whitelist.find(whitelistElem => {
        return whitelistElem.name === name;
      });

      if (found) {
        this.error.whitelist = "duplicates";
        return false;
      } else {
        return true;
      }
    },
    addWhitelistItem() {
      if (this.validateNewWhitelistElem(this.newWhitelistElem)) {
        this.config.whitelist.push(this.newWhitelistElem);
        this.newWhitelistElem = { name: "" };
        this.newWhitelistElemType = "";
      }
    },
    deleteWhitelistItem(itemToDelete) {
      this.config.whitelist = this.config.whitelist.filter(item => {
        return item.name !== itemToDelete.name;
      });
    },
    toggleCategory(toggledCategory, selected) {
      this.isLoading.toggleCategory[toggledCategory.id] = true;
      toggledCategory.selected = selected;
      let categoryFound = this.allCategories.find(category => {
        return toggledCategory.id === category.id;
      });
      categoryFound.selected = selected;
      this.saveSettings(false);
    }
  }
};
</script>

<style scoped>
.mg-left-sm {
  margin-left: 1rem;
}

.mg-left-5 {
  margin-left: 5px !important;
}

.mg-top-md {
  margin-top: 2rem;
}

.category-table {
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.bold {
  font-weight: bold;
}

.full-size {
  width: 100%;
  height: 100%;
}

.confidence {
  font-weight: bold;
}

.whitelist {
  border-left: 1px solid #ededec;
  border-right: 1px solid #ededec;
  margin: 0;
}

.whitelist-button-c {
  margin: 0;
  flex: 0.2;
}

.whitelist-button {
  width: 100%;
}

.pad-top-bottom-sm {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.whitelist-elem {
  width: 100% !important;
  font-weight: normal;
  font-size: 12px !important;
  margin: 0;
}

.font-size-normal {
  font-size: 12px !important;
}

.label-loader {
  padding-right: 0;
}

.chart-title {
  text-align: center;
}

.stats-container {
  display: table-cell !important;
  width: auto !important;
  padding: 20px !important;
  border-width: initial !important;
  border-style: none !important;
  border-color: initial !important;
  border-image: initial !important;
}

.stats-text {
  margin-top: 10px !important;
}

.category-status-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  margin-top: 0.3rem;
}
</style>
