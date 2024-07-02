/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import {Component, OnInit, ViewChild} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import { MatTableDataSource, MatSort, MatPaginator } from '@angular/material';
import { DataSource } from '@angular/cdk/table';
import { strictEqual } from 'assert';
import { LoaderComponent } from '../../loader/loader.component'

export interface Element {
  entity: string,
  values: string[],
}

@Component({
    selector: 'app-NER-configuration',
    templateUrl: './NER-configuration.component.html',
    styleUrls: ['./NER-configuration.component.css']
})

export class NERConfigurationComponent implements OnInit{
    
    disableTeam: boolean = false;
    @ViewChild(MatSort) sort: MatSort;
    @ViewChild(MatPaginator) paginator: MatPaginator;
    dataSource;
    displayedColumns = [];
    entDocLst : any = [];
    msg : string;
    msgClr : string;
    showMsgState : boolean = true;
    NERDocBkp : any = [];
    exportSuccess :boolean =false;
    enableExportButton:boolean=false;
    loading :boolean=false;
    //numberOfTags:number=10;
    numberOfTags:number;
    /**
     * Pre-defined columns list for annotation table
     */
    columnNames = [{
        id: "entity",
        value: "Tag Name"
    },{
        id: "description",
        value: "Annoted Words"
    }];
    
    constructor(private httpClient: HttpClient){}
    
    ngOnInit() {
        this.httpClient.get('/api/ner/numberOfTopics').subscribe(data=>{
          console.log('numbers of tags:',this.numberOfTags)
          this.numberOfTags= data['response'];
          //this.numberOfTags = data;
          this.httpClient.get('/api/ner/getTopicTags/'+this.numberOfTags).subscribe(data=> {
            if(data['response'] != 'failure'){
              this.entDocLst= data['response'];
              this.NERDocBkp = JSON.parse(JSON.stringify( this.entDocLst ));
             this.createTable();
            }else{
               console.warn('Could not get data from api!');
            }
          }, err=> {
            console.error('Could not get data! ,'+err)
          });
          //this.numberOfTags = event.target.value
          this.displayedColumns = this.columnNames.map(x => x.id);
        })


          
      }
      onTagsCountChanged(event: any){
        this.generateTags();
      }

      generateTags(){
        this.enableExportButton=true;
        this.loading=true;
        this.httpClient.get('/api/ner/getTopicTags/'+this.numberOfTags).subscribe(data=> {
            if(data['response'] != 'failure'){
              this.entDocLst= data['response'];
              this.NERDocBkp = JSON.parse(JSON.stringify( this.entDocLst ));
              this.createTable();
              this.loading=false;
            }else{
              console.warn('Could not get data from api!');
            }
          }, err=> {
            console.error('Could not get data! ,'+err)
          });
        this.displayedColumns = this.columnNames.map(x => x.id);

      }
    
      createTable() {
        let tableArr: Element[] = this.entDocLst;
        this.dataSource = new MatTableDataSource(tableArr);
        this.dataSource.sort = this.sort;
        this.dataSource.paginator = this.paginator;
      }

      trainNER(){
        this.msgClr = 'green';
        this.httpClient.put('http://localhost:5003/ner/api/retraining_data', null).subscribe(data => {
          if(data == 'success'){
              this.msg = 'Retraining completed successfully!';
              console.info('Retraining successfull!');
          }else{
              this.msgClr = 'red';
              this.msg = 'Could not Retrain! Please try again';
              console.warn('failure response from backend!');
          }
        }, err => {
            this.msgClr = 'red';
            this.msg = 'Retraining Failed due to some Error! Please try again later';
            console.error('Could not train! error : '+err);
        });
      }

      saveNERConfig(){
        console.log("entdoclist before is",this.entDocLst)
        let temp_lst: any=[];
        this.entDocLst.forEach(entDoc => {
          entDoc['description'].forEach(value => {
            if(typeof value != 'string')
              temp_lst.push(value['value']);
            else
              temp_lst.push(value);
          });
          entDoc['description']= temp_lst;
          temp_lst= [];
        });
        console.log("entity doc list in save",this.entDocLst)
        this.httpClient.put('/api/ner/saveTopicTags', this.entDocLst, {'responseType': 'text'}).subscribe(data => {
          if(data == 'success'){
            this.msg = 'Saved successfully!';
            this.msgClr = 'green';
            // this.NERDocBkp = JSON.parse(JSON.stringify( this.entDocLst ));
            // this.showMsgState = true;
            console.log('saveNER : success');
          }else{
            this.msgClr = 'red';
            this.msg = 'Could not Save!';
            console.warn('Could not save by api!');
          }
        }, err=> {
          this.msgClr = 'red';
          this.msg = 'Could not Save due to some Error! Try again later';
          console.error('Could not save!, : '+err);
        });
        this.showMsgState = true;
        // setTimeout(this.clearMsg, 5000)
      }

      exportToCSV() {
        // console.log("entDocLst in  before export ",this.entDocLst)    
        let temp_lst: any=[];
        this.entDocLst.forEach(entDoc => {
          entDoc['description'].forEach(value => {
            if(typeof value != 'string')
              temp_lst.push(value['value']);
            else
              temp_lst.push(value);
          });
          entDoc['description']= temp_lst;
          temp_lst= [];
        });
        this.httpClient.put('/api/ner/exportnerconfigtocsv' ,this.entDocLst ,{responseType: 'text'}).subscribe(data => {
          this.exportSuccess = true;
          const blob = new Blob([data.toString()], { type: 'text/csv' });
          const url= window.URL.createObjectURL(blob);
          console.log(url);
          //window.open(url);      
          let a = document.createElement('a');
          a.href = url;
          a.download = 'nerTopicModeling.csv';
          document.body.appendChild(a);
          a.click();        
          document.body.removeChild(a);
        },
        err => {
          console.log("failed to export to CSV");
          console.log(err);
          throw "";
        });
        this.enableExportButton=true;
      }
      
      
      setSaveChngState(){
        
      }

      clearMsg(){
        this.showMsgState= false;
      }

      updateTagName(element: Element, tag_name: string){
        element['entity'] = tag_name;
      }
}