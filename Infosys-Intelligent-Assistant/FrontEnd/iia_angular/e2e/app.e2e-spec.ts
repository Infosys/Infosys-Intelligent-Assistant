/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { MaterialDashboardAngularPage } from './app.po';

describe('material-dashboard-angular App', () => {
  let page: MaterialDashboardAngularPage;

  beforeEach(() => {
    page = new MaterialDashboardAngularPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
