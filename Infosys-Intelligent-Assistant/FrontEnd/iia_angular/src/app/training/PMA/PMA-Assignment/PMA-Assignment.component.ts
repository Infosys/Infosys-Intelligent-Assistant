/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-PMA-Assignment',
  templateUrl: './PMA-Assignment.component.html',
  styleUrls: ['./PMA-Assignment.component.css']
})
export class PMAAssignementComponent {
  Categories: string[] = [];
  private customerId: number = 1;
  datasetID: number;
  temp_list: any;
  filter_columns: any = [];
  showwordcloudflag = false;
  barwordflag: boolean = false;
  donutflag: boolean = false;
  showCloud = false;
  loading: boolean = false;
  bargraphresponse;
  barlabels: any[];
  BarNumbers: any[];
  selected_cloudtype_default = "1";
  selected_yearmonth_default: string = "year"
  selected_donut: any;
  showYearGraph: boolean = true;
  showMonthGraph: boolean = false;
  year: number;
  category: any;
  graph_type_default:string = "year"
  graph_type: string = "year"
  selected_field_default: string;
  image_src: string
  selected_year_default:number;
  selected_month_default:string;
  months:any=['January','February','March','April','May','June','July','August','September','October','November','December'];
  year_columns:any=[]
  selected_field: string;
  constructor(private httpClient: HttpClient) {
    this.donutflag = false;
  }
  ngOnInit() {    
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
        this.getCategory();
        this.getYear();
      }
    });
    this.selected_field= this.selected_field_default
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
  initial_Bar_graph(selected_year_default, selected_field_default){
    this.loading = false
    this.httpClient.get('/api/generatePMAGraph/' + this.customerId + '/' + this.datasetID + '/' +selected_year_default+ '/'+undefined+ '/' +selected_field_default,{responseType: "text"}).subscribe(data => {                
      if (data == "Success") {
        this.loading = false
        this.image_src = '/assets/video/PMA_'+this.selected_year_default+'_'+this.selected_month_default+'_'+this.selected_field+'.png'
      }
    });
  }
  PMA_redrawGraph(dropdownvalue: any) {
    this.selected_month_default=undefined;
    this.loading = true
    if (dropdownvalue != "") {
      this.loading = false
      this.selected_field = dropdownvalue as string;
    }    
  }
  handleClick(){
    this.loading = true;
    if(this.selected_field_default==undefined || this.selected_year_default==undefined){
      alert("Please provide mandatory fields.");
      this.loading=false;
    }
    else if(this.selected_month_default!==undefined){
    this.httpClient.get('/api/generatePMAGraph/' + this.customerId + '/' + this.datasetID + '/' + this.selected_year_default + '/' +this.selected_month_default+'/'+ this.selected_field,{responseType: "text"}).subscribe(data => {                
      if (data == "Success") {
        this.loading = false
        this.image_src = '/assets/video/PMA_'+this.selected_year_default+'_'+this.selected_month_default+'_'+this.selected_field+'.png'
      }
    });
    }else{
      this.httpClient.get('/api/generatePMAGraph/' + this.customerId + '/' + this.datasetID + '/' +  this.selected_year_default + '/' +this.selected_month_default + '/' + this.selected_field,{responseType: "text"}).subscribe(data => {                
        if (data == "Success") {
          this.loading = false
          this.image_src = '/assets/video/PMA_'+this.selected_year_default+'_'+this.selected_month_default+'_'+this.selected_field+'.png'
        }
      });
    }
  }
  getYear(){
    this.year_columns=[]
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
    this.selected_month_default=undefined;
    this.httpClient.get('/api/getSelctedYearData/' + this.customerId + '/' + this.datasetID , { responseType: 'json' }).subscribe(data => {      
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          //console.log(this.temp_list[i]);
        }
    }
  });
}
}
