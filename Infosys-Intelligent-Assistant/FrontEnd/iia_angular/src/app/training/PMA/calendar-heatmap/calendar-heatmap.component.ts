/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-calendar-heatmap',
  templateUrl: './calendar-heatmap.component.html',
  styleUrls: ['./calendar-heatmap.component.css']
})
export class CalendarHeatmapComponent implements OnInit {
  private customerId: number = 1;
  public datasetID: number;
  filter_columns: any = [];
  loading: boolean;
  image_src: string;
  default_selectedYear: string = "2019";
  years: any[] = [];
  showHeatMap: boolean = true;
  filter_assignment_group: any = ["All"];
  temp_list: any = [];
  selected_field_default: string;
  selected_col: string = "assignment_group";
  selectedDate: string;
  showPieChart: boolean = false;
  showEmpty: boolean = false;
  disable: boolean = true;
  year_columns: any = []
  selectedYear: string;
  image_src_pie: string;
  disable_heatmap: boolean = true;
  constructor(private httpClient: HttpClient) { }
  ngOnInit() {
    for (let i = 2017; i <= 2021; i++) {
      this.years.push(i.toString())
    }
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
      }
      this.getAssignmentGroupNameList();
      this.getYear();
    });
  }
  getAssignmentGroupNameList() {
    this.httpClient.get('/api/getSelctedColumnData/' + this.customerId + '/' + this.datasetID + '/' + this.selected_col, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        this.filter_assignment_group = []
        for (let i = 0; i < this.temp_list.length; i++) {
          this.filter_assignment_group.push(this.temp_list[i]);
        }
      }
    });
  }
  default_heat_map() {
    this.loading = false
    this.httpClient.get('/api/generateHeatMap/' + this.customerId + '/' + this.datasetID + '/' + this.selectedYear + '/' + this.selected_field_default, { responseType: "text" }).subscribe(data => {
      if (data == "Success") {
        this.loading = false
        this.image_src = '/assets/video/heat_map_' + this.selected_field_default + '_' + this.selectedYear + '.jpg'
      }
      else {
        console.log("not generated.......................")
      }
    });
  }
  generateHeatMap() {
    this.loading = true;
    this.showEmpty = false;
    this.showHeatMap = true;
    this.showPieChart = false
    this.httpClient.get('/api/generateHeatMap/' + this.customerId + '/' + this.datasetID + '/' + this.selectedYear + '/' + this.selected_field_default, { responseType: "text" }).subscribe(data => {
      if (data == "Success") {
        this.loading = false
        this.image_src = '/assets/video/heat_map_' + this.selected_field_default + '_' + this.selectedYear + '.jpg'
      }
    });
  }
  category_selected() {
    if (this.selectedYear != undefined) {
      this.disable_heatmap = false;
    } else {
      this.disable_heatmap = true;
    }
  }
  year_selected() {
    if (this.selected_field_default != undefined) {
      this.disable_heatmap = false;
    } else {
      this.disable_heatmap = true;
    }
  }
  Re_generateHeatMap() {
    this.loading = true
    this.showEmpty = false
    this.showHeatMap = true
    this.showPieChart = false
    this.httpClient.get('/api/generateHeatMap/' + this.customerId + '/' + this.datasetID + '/' + this.selectedYear + '/' + this.selected_field_default, { responseType: "text" }).subscribe(data => {
      if (data == "Success") {
        this.loading = false
        this.image_src = '/assets/video/heat_map_' + this.selected_field_default + '_' + this.selectedYear + '.jpg'
      }
      else {
        console.log("not generated.......................")
      }
    });
  }
  getDate(e) {
    this.disable = false
    this.selectedDate = e.target.value
    console.log(this.selectedDate)
  }
  generatePieChart() {
    this.loading = true
    this.showHeatMap = true
    this.showPieChart = true
    this.httpClient.get('/api/generatePieChart/' + this.customerId + '/' + this.datasetID + '/' + this.selectedDate, { responseType: "text" }).subscribe(data => {
      if (data == "Success") {
        this.showEmpty = false
        this.loading = false
        this.image_src_pie = '/assets/video/pie_Chart' + this.selectedDate + '.jpg';
      }
      else if (data == "Empty") {
        this.loading = false
        this.showHeatMap = false
        this.showPieChart = false
        this.showEmpty = true;
      }
    });
  }
  getYear() {
    this.year_columns = [];
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
    this.httpClient.get('/api/getSelctedYearData/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
        }
      }
    });
  }
}