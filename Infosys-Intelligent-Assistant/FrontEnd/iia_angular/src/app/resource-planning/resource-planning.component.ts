/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit,HostListener,ViewChild } from '@angular/core';
import { RosterFileUploadComponent } from '../resource-planning/roster-file-upload/roster-file-upload.component'
import { MatTabGroup, MatTabHeader, MatTab, MatTabChangeEvent } from '@angular/material';
@Component({
  selector: 'app-resource-planning',
  templateUrl: './resource-planning.component.html',
  styleUrls: ['./resource-planning.component.css']
})
export class ResourcePlanningComponent implements OnInit {
  @ViewChild('tabs') tabsmat: MatTabGroup;
  index=0;
  constructor() { }
  ngOnInit() {
    this.tabsmat._handleClick = this.interceptTabChange.bind(this);
  }
  interceptTabChange(tab: MatTab, tabHeader: MatTabHeader, idx: number) {
    const result = confirm(`If you have any unsaved changes, please click on cancel to stay on same page. Else click on OK to navigate to another page`);
    return (
      result &&
      MatTabGroup.prototype._handleClick.apply(this.tabsmat, arguments)
    );
  }
  tabChanged = (tabChangeEvent: MatTabChangeEvent): void => {
    this.index = tabChangeEvent.index;
  }
}
