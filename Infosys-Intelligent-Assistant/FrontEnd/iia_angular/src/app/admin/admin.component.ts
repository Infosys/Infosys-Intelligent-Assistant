/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { OnInit, Component, ViewChild } from '@angular/core'
import { MatTabGroup, MatTabHeader, MatTab, MatTabChangeEvent } from '@angular/material';
@Component({
  selector: 'app-admin',
  templateUrl: 'admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  @ViewChild('tabs') tabsmat: MatTabGroup;
  index = 0;
  constructor() { }
  ngOnInit() {
  }
  tabChanged = (tabChangeEvent: MatTabChangeEvent): void => {
    this.index = tabChangeEvent.index;
  }
}