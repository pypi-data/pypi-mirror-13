/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

this.EXPORTED_SYMBOLS = [ "WebNotifications" ];

const {classes: Cc, interfaces: Ci, utils: Cu} = Components;

Cu.import("resource://gre/modules/Services.jsm");
Cu.import("resource://gre/modules/devtools/Console.jsm");
Cu.import("resource://testing-common/BrowserTestUtils.jsm");

this.DevEdition = {
  _testCases: {
    titleOnly: {
      title: "Title-Only",
    },
  },

  init(libDir) {
    for (let testCaseName of Object.keys(this._testCases)) {
      let testCase = this._testCases[testCase];
      this.configurations[testCaseName] = {
        applyConfig(deferred) {
          deferred.resolve(testCaseName);
        },
      };
    }
  },

  configurations: {},
};
