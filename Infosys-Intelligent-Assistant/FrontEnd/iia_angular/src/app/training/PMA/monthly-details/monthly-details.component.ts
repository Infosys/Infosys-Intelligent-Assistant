/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { Chart } from 'chart.js';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ChartsModule } from 'ng2-charts';
@Component({
  selector: 'app-monthly-details',
  templateUrl: './monthly-details.component.html',
  styleUrls: ['./monthly-details.component.css']
})
export class MonthlyDetailComponent implements OnInit {
  public monthslist: string[] = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  yearslist: any = [];
  Categories: string[] = [];
  private customerId: number = 1;
  datasetID: number;
  temp_list: any;
  filter_columns: any = [];
  linewordflag: boolean = false;
  showCloud = false;
  linegraphresponse;
  loading: boolean = false;
  labels: any[];
  lineNumbers: any[];
  public chartColors: any[] = [
    {
      backgroundColor: 'rgba(105, 0, 132, .2)',
      borderColor: 'rgba(200, 99, 132, .7)',
      borderWidth: 2,
    },
    {
      backgroundColor: 'rgba(0, 137, 132, .2)',
      borderColor: 'rgba(0, 10, 130, .7)',
      borderWidth: 2,
    }];
  private myArrayNumber: any = [0, 90];
  public lineChartOptions: any = {
    responsive: true,
  }
  public lineChartLabels: string[] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  public lineChartType: string = 'line';
  public lineChartLegend: boolean = true;
  public lineChartData: any[] = [{ data: [65, 59, 80, 81, 56, 55, 40, 90, 59, 80, 20, 60], label: 'My First dataset' },
  { data: [28, 48, 40, 19, 86, 27, 90, 80, 70, 80, 50, 67, 30], label: 'My Second dataset' }];
  private myArrayColor: any = ["#00695c", "#1C2331", "#d50000", "#1b5e20", "#e65100", "#212121", "#3e2723",
    "#000000", "#1c2331"];
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
  getYear() {
    this.yearslist = []
    this.httpClient.get('/api/getSelctedYearData/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          this.yearslist.push(this.temp_list[i]);
        }
      }
    });
  }
  public chartHovered(e: any): void {
    console.log(e);
  }
  private selected_from: string = "";
  private selected_upto: string = "";
  tagCloudData = [];
  tagWordCloud: any;
  wordcloudsample: any = {};
  xAxisValue: any;
  yAxisValue: any;
  numberOfWords: number = 30;
  cloudType: string = 'Unigram';
  // wordcloud methods 
  onWordsCountChanged(event: any) {
    this.numberOfWords = event.target.value
    this.displayWordCloud_PMA();
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
  constructor(private httpClient: HttpClient) {
  }
  ngOnInit() {
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
        this.getYear();
      }
    });
  }
  showWordsclicked() {
    if (this.linewordflag == false) {
      this.linewordflag = true;
    }
    else {
      this.linewordflag = false;
    }
  }
  rememberOption(dropdownvalue: any) {
    if (dropdownvalue != "") {
      this.selected_from = dropdownvalue as string;
      if ((this.selected_from && this.selected_upto) != "") {
        this.PMA_drawGraph(this.selected_from, this.selected_upto);
      }
    }
  }
  PMA_redrawToGraph(dropdownvalue: any) {
    this.showCloud = false;
    if (dropdownvalue != "") {
      this.selected_upto = dropdownvalue as string;
      if ((this.selected_from && this.selected_upto) != "") {
        this.PMA_drawGraph(this.selected_from, this.selected_upto);
      }
    }
  }
  ////need to change selected_from below logic while api calling with both from and to dates
  PMA_drawGraph(fromyear: any, toyear: any) {
    this.httpClient.get('/api/monthlyTrendPMA/' + this.customerId + '/' + this.datasetID + '/' + fromyear + '/' + toyear).subscribe(data => {
      if (data) {
        this.linegraphresponse = data;
        let sorted_list_2018: any = [];
        let sorted_list_2019: any = [];
        let sorted_count_2018: any = [];
        let sorted_count_2019: any = [];
        let sample_list: any = [];
        let sample_list_2019: any = [];
        var months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"];
        for (var key in this.linegraphresponse) {
          if (key.includes(fromyear)) {
            let month = key.split(':')[1];
            sample_list.push({ 'month': month, 'value': this.linegraphresponse[key] });
          }
          else if (key.includes(toyear)) {
            let month = key.split(':')[1];
            sample_list_2019.push({ 'month': month, 'value': this.linegraphresponse[key] });
          }
        }
        const allMonths = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"];
        let result1 = [];
        let result2 = [];
        allMonths.forEach(mon => {
          const item = sample_list_2019.find(item => item.month === mon);
          if (item) {
            result2.push(item);
          } else {
            result2.push({ month: mon, value: 0 });
          }
        })
        allMonths.forEach(mon => {
          const item = sample_list.find(item => item.month === mon);
          if (item) {
            result1.push(item);
          } else {
            result1.push({ month: mon, value: 0 });
          }
        })
        sample_list = result1;
        sample_list_2019 = result2;
        sorted_list_2018 = sample_list.sort(function (a, b) {
          return months.indexOf(a.month)
            - months.indexOf(b.month);
        });
        sorted_list_2019 = sample_list_2019.sort(function (a, b) {
          return months.indexOf(a.month)
            - months.indexOf(b.month);
        });
        for (let entry of sorted_list_2018) {
          sorted_count_2018.push(entry['value']);
        }
        for (let entry of sorted_list_2019) {
          sorted_count_2019.push(entry['value']);
        }
        this.lineChartData = [{ data: sorted_count_2018, label: this.selected_from + ' dataset' }, { data: sorted_count_2019, label: this.selected_upto + ' dataset' }];
      }
    });
  }
  PMA_clickbar() {
  }
  public chartClicked_PMA(e: any): void {
    this.showCloud = true;
    if (e.active.length > 0) {
      this.yAxisValue = e.active[0]._chart.config.data.labels[e.active[0]._index];
      this.xAxisValue = e.active[0]._chart.config.data.datasets[0].data[e.active[0]._index];
      this.displayWordCloud_PMA();
    }
  }
  //for displaying word cloud we need only graph response so calling same API as Drawing Graph
  displayWordCloud_PMA() {
    this.loading = true;
    this.httpClient.get('/api/PMAdisplayGraph/' + this.customerId + '/' + this.datasetID + '/' + this.selected_from).subscribe(data => {
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
}