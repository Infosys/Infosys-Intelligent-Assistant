/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { HttpClient } from '@angular/common/http';
import { ChartsModule } from 'ng2-charts/ng2-charts';
import { Chart, ChartOptions } from 'chart.js';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import * as pluginDataLabels from 'chartjs-plugin-labels'
import 'chart.js'
import { MatInputModule } from '@angular/material'
@Component({
  selector: 'app-pie-analysis',
  templateUrl: './pie-analysis.component.html',
  styleUrls: ['./pie-analysis.component.css']
})
export class PieAnalysisComponent {
  Categories: string[] = [];
  private customerId: number = 1;
  public datasetID: number;
  temp_list: any;
  filter_columns: any = [];
  piewordflag: boolean = false;
  showCloud = false;
  piegraphresponse;
  loading: boolean = false;
  selected_cloudtype_default: string;
  selected_field_default: string;
  selected_pie_Part: any;
  selected_year_default: number;
  selected_month_default: string;
  labels: any[];
  showEmpty: boolean = false;
  year_columns: any = []
  months: any = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  pieNumbers: any[];
  public chartColors: any[] = [
    {
      backgroundColor: ["#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b"]
    }];
  private myArrayNumber: any = [0, 90];
  //pie chart data
  public pieChartOptions: ChartOptions = {
    responsive: true,
    plugins: {
      labels: {
        render: 'label',
        fontSize: 12,
        fontColor: '#000',
        fontFamily: 'Roboto, Helvetica, Arial, sans-serif',
        position: 'outside',
        precision: 2
      },
      datalabels: {
        formatter: (value, ctx) => {
          const label = ctx.chart.data.labels[ctx.dataIndex];
          return label;
        },
      },
    }
  }
  public pieChartLabels: string[] = ["select any category to show Analysis "];
  public pieChartType: string = 'pie';
  public pieChartLegend: boolean = true;
  public pieChartData: any[] = [{ data: [100] }];
  public pieindexLabel: string = 'Test';
  private myArrayColor: any = ["#00695c", "#1C2331", "#d50000", "#1b5e20", "#e65100", "#212121", "#3e2723",
    "#000000", "#1c2331"];
  public pieChartPlugins = [pluginDataLabels];
  //for word cloud 
  ZoomOnHoverOptions = {
    scale: 1.6, // Elements will become 130 % of current zize on hover
    transitionTime: 0.3, // it will take 1.2 seconds until the zoom level defined in scale property has been reached
    delay: 0.1 // Zoom will take affect after 0.8 seconds
  };
  cloudoptions: CloudOptions = {
    // if width is between 0 and 1 it will be set to the size of the upper element multiplied by the value 
    width: 0.8,
    height: 450,
    overflow: false,
    randomizeAngle: false,
    zoomOnHover: this.ZoomOnHoverOptions,
    realignOnResize: true,
  };
  public chartHovered(e: any): void {
    console.log(e);
  }
  private selected_field: string;
  tagCloudData = [];
  tagWordCloud: any;
  wordcloudsample: any = {};
  xAxisValue: any;
  yAxisValue: any;
  numberOfWords: number = 30;
  cloudType: string = 'Bigram';
  // wordcloud methods 
  onWordsCountChanged(event: any) {
    this.numberOfWords = event.target.value
    this.displayWordCloud_PMA(this.yAxisValue);
  }
  cloudTypeChanged(dropdownvalue: any) {
    console.log(dropdownvalue);
    if (dropdownvalue == "1") {
      this.cloudType = "Bigram";
    }
    else {
      this.cloudType = "Unigram";
    }
  }
  constructor(private httpClient: HttpClient) { }
  ngOnInit() {
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
        this.getCategory();
        this.getYear();
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
  getCategory() {
    this.filter_columns = []
    this.httpClient.get('/api/piecategoryname/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          this.filter_columns.push(this.temp_list[i]);
        }
      }
    });
  }
  PMA_redrawGraph(dropdownvalue: any) {
    this.showCloud = false;
    if (this.piewordflag == true) {
      this.piewordflag = false;
    }
    if (dropdownvalue != "") {
      this.selected_field = dropdownvalue as string;
    }
  }
  PMA_drawGraph() {
    this.loading = true;
    this.httpClient.get('/api/PMAdisplayPieGraph/' + this.customerId + '/' + this.datasetID + '/' + this.selected_field + '/' + this.selected_year_default + '/' + undefined).subscribe(data => {
      if (data) {
        this.loading = false;
        this.showEmpty = false;
        this.labels = [];
        this.pieNumbers = [];
        this.piegraphresponse = data;
        for (var key in this.piegraphresponse) {
          this.labels.push([key]);
          this.pieNumbers.push(this.piegraphresponse[key])
        }
        this.pieChartData.forEach((dataset, index) => {
          this.pieChartData[index] = Object.assign({}, this.pieChartData[index], {
            data: this.pieNumbers,
            label: this.selected_field
          });
        });
        this.pieChartLabels = this.labels;
        var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
      }
      if (Object.keys(data).length === 0) {
        this.showEmpty = true;
      }
    });
  }
  PMA_clickbar() {
  }
  public chartClicked_PMA(e: any): void {
    console.log("pie chart data on click...." + this.piegraphresponse);
    console.log(e);
    this.showCloud = true;
    if (e.active.length > 0) {
      if (this.piewordflag == false) {
        this.piewordflag = true;
      }
      this.yAxisValue = e.active[0]._chart.config.data.labels[e.active[0]._index];
      this.xAxisValue = e.active[0]._chart.config.data.datasets[0].data[e.active[0]._index];
      this.displayWordCloud_PMA(this.yAxisValue);
      this.selected_pie_Part = this.yAxisValue;
    }
  }
  handleClick() {
    this.loading = true;
    if (this.selected_field_default == undefined || this.selected_cloudtype_default == undefined || this.selected_year_default == undefined) {
      alert("Please provide mandatory fields.");
      this.loading = false;
    }
    else if (this.selected_month_default !== undefined) {
      this.httpClient.get('/api/PMAdisplayPieGraph/' + this.customerId + '/' + this.datasetID + '/' + this.selected_field + '/' + this.selected_year_default + '/' + this.selected_month_default).subscribe(data => {
        if (data) {
          this.loading = false;
          this.showEmpty = false;
          this.labels = [];
          this.pieNumbers = [];
          this.piegraphresponse = data;
          for (var key in this.piegraphresponse) {
            this.labels.push([key]);
            this.pieNumbers.push(this.piegraphresponse[key])
          }
          this.pieChartData.forEach((dataset, index) => {
            this.pieChartData[index] = Object.assign({}, this.pieChartData[index], {
              data: this.pieNumbers,
              label: this.selected_field
            });
          });
          this.pieChartLabels = this.labels;
          var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
        }
        if (Object.keys(data).length === 0) {
          this.showEmpty = true;
        }
      });
    } else {
      this.httpClient.get('/api/PMAdisplayPieGraph/' + this.customerId + '/' + this.datasetID + '/' + this.selected_field + '/' + this.selected_year_default + '/' + undefined).subscribe(data => {
        if (data) {
          this.loading = false;
          this.showEmpty = false;
          this.labels = [];
          this.pieNumbers = [];
          this.piegraphresponse = data;
          for (var key in this.piegraphresponse) {
            this.labels.push([key]);
            this.pieNumbers.push(this.piegraphresponse[key])
          }
          this.pieChartData.forEach((dataset, index) => {
            this.pieChartData[index] = Object.assign({}, this.pieChartData[index], {
              data: this.pieNumbers,
              label: this.selected_field
            });
          });
          this.pieChartLabels = this.labels;
          var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
        }
        if (Object.keys(data).length === 0) {
          this.showEmpty = true;
        }
      });
    }
  }
  displayWordCloud_PMA(yaxisselected_field_value: any) {
    if (this.selected_field_default != undefined) {
      if (yaxisselected_field_value != undefined) {
        this.loading = true;
        let unassigned_flag = 'false';
        if (yaxisselected_field_value == "Unassigned") {
          unassigned_flag = 'true'
        }
        this.httpClient.get('/api/PMAdisplayPieWordCloud/' + this.customerId + '/' + this.datasetID + '/' + this.selected_field + '/' + yaxisselected_field_value + '/' + unassigned_flag + '/' + this.numberOfWords + '/' + this.cloudType).subscribe(data => {
          if (data) {
            this.loading = false;
            this.tagCloudData = [];
            this.wordcloudsample = data;
            for (var key in this.wordcloudsample) {
              var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
              this.tagCloudData.push({ text: key + '(' + this.wordcloudsample[key] + ')', weight: (this.wordcloudsample[key]), color: randomItem });
            }
          }
        });
        this.showCloud = true;
      }
    } else {
      console.warn("Choosen filed value is empty!");
      alert("Choosen filed value is empty!")
    }
  }
  changeYear(value) {
    console.log(value)
    this.selected_month_default = null;
    this.httpClient.get('/api/getSelctedYearData/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          console.log(this.temp_list[i]);
        }
      }
    });
  }
}