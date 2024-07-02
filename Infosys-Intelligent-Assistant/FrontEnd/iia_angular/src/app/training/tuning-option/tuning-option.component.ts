/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { switchMap } from 'rxjs/operators';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { TagInputModule } from 'ngx-chips';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'; // this is needed!
import { ChartsModule } from 'ng2-charts';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { Chart } from 'chart.js';
import { ViewEncapsulation } from '@angular/core';
import { WhitelistedWordsComponent } from './whitelisted-words/whitelisted-words.component';
@Component({
  selector: 'app-tuning-option',
  templateUrl: './tuning-option.component.html',
  styleUrls: ['./tuning-option.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class TuningOptionComponent implements OnInit {
  @ViewChild("Unigram") canvas: ElementRef;
  lineChartColors;
  @Input() dataToTakeAsInput: any;
  showCloud = false;
  closeResult: string;
  wordcloudsample: any = {};
  tagCloudData = [];
  tagWordCloud: any;
  items: any = [];
  bargraphresponse;
  labels: any[];
  BarNumbers: any[];
  private customerId: number;
  datasetID: number;
  private predicted_field: string;
  xAxisValue: any;
  yAxisValue: any;
  Summaries: string[] = [];
  cloudType: string = 'Unigram';
  approvedStopwords: any;
  numberOfWords: number = 30;
  showStopWords: boolean = true;
  numberFormat: any;
  constructor(private httpClient: HttpClient, public activeModal: NgbActiveModal, private modalService: NgbModal) {
    TagInputModule.withDefaults({
      tagInput: {
        placeholder: 'Add a new stopword',
        // add here other default values for tag-input
      },
      dropdown: {
        displayBy: 'my-display-value',
        // add here other default values for tag-input-dropdown
      }
    });
  }
  ZoomOnHoverOptions = {
    scale: 1.6, // Elements will become 130 % of current zize on hover
    transitionTime: 0.3, // it will take 1.2 seconds until the zoom level defined in scale property has been reached
    delay: 0.1 // Zoom will take affect after 0.8 seconds
  };
  cloudoptions: CloudOptions = {
    // if width is between 0 and 1 it will be set to the size of the upper element multiplied by the value 
    width: 0.8,
    height: 450,
    overflow: true,
    randomizeAngle: false,
    zoomOnHover: this.ZoomOnHoverOptions,
    realignOnResize: true,
  };
  ngOnInit() {
  }
  private myArrayColor: any = ["#00695c", "#1C2331", "#d50000", "#1b5e20", "#e65100", "#212121", "#3e2723",
    "#000000", "#1c2331"];
  private myArrayNumber: any = [0, 90];
  //Bar chart data
  public barChartOptions: any = {
    scaleShowHorizontalLines: true,
    scaleShowVerticalLines: false,
    responsive: true,
    scales: {
      xAxes: [{
        ticks: {
          max: 100,
          maxRotation: 90,
          autoSkip: false,
          fontSize: 10,
          offsetGridLines: true
        }
      }],
      yAxes: [{
        ticks: {
          maxRotation: 90 // angle in degrees
        }
      }]
    },
    plugins: {
      labels: {
        render: () => { }
      },
      datalabels: {
      },
    }
  }
  public chartColors: any[] = [
    {
      backgroundColor: ["#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b",
        "#FF7360", "#6FC8CE", "#69f0ae", "#5d4037", "#aa66cc", "#880e4f", "#00897b"]
    }];
  public barChartLabels: string[];
  public barChartType: string = 'bar';
  public barChartLegend: boolean = false;
  public barChartData: any[] = [{ data: [147, 104, 175, 266, 28, 135, 137, 37, 45] }];
  drawGraph() {
    this.httpClient.get('/api/displayGraph/' + this.customerId + '/' + this.datasetID + '/' + this.predicted_field).subscribe(data => {
      if (data) {
        this.labels = [];
        this.BarNumbers = [];
        this.bargraphresponse = data;
        for (var key in this.bargraphresponse) {
          this.labels.push(key);
          this.BarNumbers.push(this.bargraphresponse[key])
        }
        this.barChartData.forEach((dataset, index) => {
          this.barChartData[index] = Object.assign({}, this.barChartData[index], {
            data: this.BarNumbers,
            label: this.predicted_field
          });
        });
        this.barChartLabels = this.labels;
        var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
      }
    });
    this.httpClient.get('/api/displayStopWords/' + this.customerId + '/' + this.datasetID).subscribe(data => {
      if (data) {
        this.items = data;
      }
    });
  }
  public chartClicked(e: any): void {
    this.showCloud = true;
    if (e.active.length > 0) {
      this.xAxisValue = e.active[0]._chart.config.data.labels[e.active[0]._index];
      this.yAxisValue = e.active[0]._chart.config.data.datasets[0].data[e.active[0]._index];
      this.displayWordCloud();
    }
  }
  displayWordCloud() {
    this.httpClient.get('/api/displayWordCloud/' + this.customerId + '/' + this.datasetID + '/' + this.predicted_field + '/' + this.xAxisValue + '/' + this.numberOfWords + '/' + this.cloudType).subscribe(data => {
      if (data) {
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
  cloudTypeChanged(dropdownvalue: any) {
    if (dropdownvalue == "1") {
      this.cloudType = "Bigram";
      this.showStopWords = false;
    }
    else {
      this.cloudType = "Unigram";
      this.showStopWords = true;
    }
    this.httpClient.get('/api/displayWordCloud/' + this.customerId + '/' + this.datasetID + '/' + this.predicted_field + '/' + this.xAxisValue + '/' + this.numberOfWords + '/' + this.cloudType).subscribe(data => {
      if (data) {
        this.tagCloudData = [];
        this.wordcloudsample = data;
        console.log("display word cloud...", data);
        for (var key in this.wordcloudsample) {
          var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
          this.tagCloudData.push({ text: key + '(' + this.wordcloudsample[key] + ')', weight: (this.wordcloudsample[key] / 20), color: randomItem });
        }
      }
    });
    this.showCloud = true;
  }
  public chartHovered(e: any): void {
  }
  redrawGraph(dropdownvalue: any) {
    this.showCloud = false;
    if (dropdownvalue != "") {
      this.predicted_field = dropdownvalue as string;
      this.drawGraph();
    }
  }
  logClicked(e: any) {
    if (this.cloudType != "Bigram") {
      if (!this.items.find(i => i == e.text)) {
        this.items.push(e.text.split("(")[0]);
      }
    }
  }
  approveStopWords() {
    this.approvedStopwords = [];
    let stopwords = [];
    for (let i = 0; i < this.items.length; i++) {
      JSON.stringify(this.items[i]);
      if (this.items[i]["value"] != undefined) {
        stopwords.push(this.items[i]["value"]);
      }
      else {
        stopwords.push(this.items[i]);
      }
    }
    this.approvedStopwords = { 'stopwords': stopwords };
    this.httpClient.put('/api/saveStopWords/' + this.customerId + "/" + this.datasetID, this.approvedStopwords,
      { responseType: 'text' }).subscribe(msg => {
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  onWordsCountChanged(event: any) {
    this.numberFormat = /^[0-9]{1,3}$/;
    this.numberOfWords = event.target.value
    if (!this.numberFormat.test(this.numberOfWords)) {
      alert('Wrong input! Allowed value limit: 1 - 999');
      return;
    }
    this.displayWordCloud();
  }
  openWhitelistedmodal() {
    const modalRef = this.modalService.open(WhitelistedWordsComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
    let dataPassToChild: any = {};
    dataPassToChild['PredictedValues'] = this.labels;
    dataPassToChild['DatasetID'] = this.datasetID;
    dataPassToChild['PredictedField'] = this.predicted_field;
    (<WhitelistedWordsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  downloadKeywordReport() {
    this.httpClient.get('/api/getWordCloudList/' + this.customerId + '/' + this.datasetID + '/' + this.predicted_field + '/' + this.numberOfWords + '/' + this.cloudType, { responseType: 'text' }).subscribe(data => {
      const blob = new Blob([data.toString()], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      let a = document.createElement('a');
      a.href = url;
      a.download = 'KeywordReport.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
  }
}
