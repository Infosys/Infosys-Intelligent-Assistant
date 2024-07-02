/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-line-graph',
  templateUrl: './line-graph.component.html',
  styleUrls: ['./line-graph.component.scss']
})
export class LineGraphComponent implements OnInit {
  Categories: string[] = [];
  private customerId: number = 1;
  datasetID: number;
  temp_list: any;
  loading: boolean = false;
  filter_columns: any = [];
  showYearGraph: boolean = true;
  showMonthGraph: boolean = false;
  year: number;
  selected_yearmonth_default: string = "year"
  category: any;
  graph_type_default: string = "year"
  graph_type: string = "year"
  selected_field_default: string;
  image_src: string;
  selected_year_default: number;
  selected_month_default: string;
  year_columns: any = []
  show_values = false
  selected_group_list = ["All"]
  selected_names: any = []
  selected_group_str: string = ""
  selected_names_grp: any = []
  months: any = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  one: any;
  currentlyDisabled: string;
  selected_field: string;
  constructor(private httpClient: HttpClient) {
  }
  ngOnInit() {
    this.selected_field = this.selected_field_default;
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
        this.getCategory();
        this.getYear();
      }
    });
  }
  onChangeDisable() {
    if (this.selected_field || this.selected_field_default || this.selected_month_default || this.selected_year_default) {
      this.currentlyDisabled = 'two';
    } else {
      this.currentlyDisabled = '';
    }
  }
  getSelectedOptions(some) {
    this.selected_names_grp = some.value
  }
  handleClick() {
    this.loading = true
    if (this.selected_field_default == undefined || this.selected_names == undefined || this.selected_year_default == undefined) {
      alert("Please provide mandatory fields.");
      this.loading = false;
    } else {
      let sendData = {
        selected_month: this.selected_month_default,
        selected_year: this.selected_year_default,
        selected_field: this.selected_field,
        selected_groups: this.selected_names
      }
      this.httpClient.post('/api/generatePMALineGraph', sendData, { responseType: "text" }).subscribe(data => {
        if (data == "Success") {
          this.loading = false
          this.image_src = '/assets/video/PMA_Line_' + this.selected_year_default + '_' + this.selected_month_default + '_' + this.selected_field + '_' + this.selected_names.join('_') + '.png'
        }
      });
    }
  }
  getGroupNameList(selected_col) {
    this.httpClient.get('/api/getSelctedColumnData/' + this.customerId + '/' + this.datasetID + "/" + selected_col, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.selected_group_list = []
        this.loading = false
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          this.selected_group_list.push(this.temp_list[i]);
        }
      }
    });
  }
  initial_line_graph() {
    console.log("initial line graph")
    this.loading = true
    let sendData = {
      selected_month: null,
      selected_year: this.selected_year_default,
      selected_field: this.selected_field,
      selected_groups: this.selected_names
    }
    this.httpClient.post('/api/generatePMALineGraph', sendData, { responseType: "text" }).subscribe(data => {
      if (data == "Success") {
        this.image_src = '/assets/video/PMA_Line_' + this.selected_year_default + '_' + this.selected_month_default + '_' + this.selected_field + '_' + this.selected_names.join('_') + '.png'
        this.loading = false
        console.log("Graph generated successfully");
      }
    });
  }
  PMA_redrawLineGraph(dropdownvalue: any) {
    this.loading = true
    this.show_values = true
    this.selected_names = []
    if (dropdownvalue != "") {
      this.selected_field = dropdownvalue
      this.getGroupNameList(this.selected_field)
      let sendData = {
        graph_type: this.graph_type,
        selected_field: this.selected_field,
        selected_groups: this.selected_names
      }
    }
  }
  getCategory() {
    this.httpClient.get('/api/barcategoryname/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          this.filter_columns.push(this.temp_list[i]);
        }
      }
    });
  }
  getYear() {
    this.year_columns = []
    this.httpClient.get('/api/getSelctedYearData/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          this.year_columns.push(this.temp_list[i]);
        }
      }
    });
  }
  PMAtypeChanged(value) {
    this.selected_month_default = undefined;
    this.httpClient.get('/api/getSelctedYearData/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
        }
      }
    });
  }
  PMAtypeChangedMonth(dropdownvalue: any) {
  }
}
