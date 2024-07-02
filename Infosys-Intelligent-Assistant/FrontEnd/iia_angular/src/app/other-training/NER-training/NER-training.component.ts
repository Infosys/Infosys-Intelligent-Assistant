/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild } from '@angular/core';
import { MatTableDataSource, MatSort, MatPaginator } from '@angular/material';
import { DataSource } from '@angular/cdk/table';
import { HttpClient } from '@angular/common/http';
import { strictEqual } from 'assert';
import { text } from '../../../../node_modules/@angular/core/src/render3';

export interface Element {
    entity: string,
    description: string[],
  }

  export interface UserData {
    entity: string,
    description: string[],
    // status:string;
  }

@Component({
    selector : 'app-NER-training',
    templateUrl : './NER-training.component.html',
    styleUrls : ['./NER-training.component.css']
})
export class NERTrainingComponent implements OnInit {
  disableTeam: boolean = false;
  loading: boolean = false;
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  dataSource;
  displayedColumns = [];
  entDocLst : any = [];
  msg : string;
  msgClr : string;
  showMsgState : boolean = true;
  NERDocBkp : any = [];
  NERDocBkp2 : any = [];
  saveSuccess:boolean=false;
  newtag:boolean=false;
  newtaglst:any=[]
   public envInfo:UserData[]=[];

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

  constructor(private httpClient: HttpClient) {}
  ngOnInit() {
    // this.httpClient.get('http://localhost:5003/ner/api/get_annoted_data').subscribe(data => {
    //     this.entDocLst = data;
    //     this.NERDocBkp = JSON.parse(JSON.stringify( this.entDocLst ));
    //     this.createTable();
    // });
      this.httpClient.get('/api/ner/getAnnotationTags').subscribe(data=> {
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
    this.displayedColumns = this.columnNames.map(x => x.id);
  }

  addElement() {
    this.newtag=true;
    this.saveSuccess=false;
    // this.getScriptNames()
    this.envInfo.push({entity:'',description:[]})
    this.dataSource = new MatTableDataSource(this.envInfo);
    console.log("this.envInfo is ",this.envInfo)
    console.log("this.dataSource is ",this.dataSource)


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


  saveNER(){
    // alert("in saveNER")
if(this.newtag==true){

  console.log("envInfo",this.envInfo)
 let data=this.envInfo;
 let temp_lst: any=[];
 let modifiedState: boolean= false;
  // console.log("datasource is ",this.dataSource)
  // console.log("type of ",typeof(data))


  for (let key in data) {
    // console.log("keys of data  are ", key);//predicting fields will come in key here 
    // console.log("values of data  are ", data[key])
    // console.log("values of data  are ", typeof(data[key]))
    this.newtaglst.push(data[key])
     console.log(" new tag list is ",this.newtaglst)
    
  }
  console.log("final new tag list is ",this.newtaglst)
  this.NERDocBkp2 = JSON.parse(JSON.stringify( this.entDocLst ));
  this.newtaglst.forEach(tagDoc => {
    tagDoc['description'].forEach(value => {
      if(typeof value != 'string'){
        modifiedState= true;
        temp_lst.push(value['value']);
      }else
        temp_lst.push(value);
    });
    tagDoc['description']= temp_lst;
    temp_lst= [];
  });
  if(!modifiedState){
    this.newtaglst.forEach(tagDoc=> {
      this.NERDocBkp2.forEach(entDocBkp=> {
        if(tagDoc['entity'] == entDocBkp['entity'])
          if(tagDoc['description'].length != entDocBkp['description'].length)
            modifiedState= true;
      });
    });
  }

  console.log("type of final new tag list is ",typeof(this.newtaglst))
  this.httpClient.put('/api/ner/saveNerTags/'+this.newtag,this.newtaglst,{responseType:'text'}).subscribe(data=>{
    if(data == 'success'){
      this.msg = 'Saved successfully!';
      this.msgClr = 'green';
      // this.NERDocBkp = JSON.parse(JSON.stringify( this.entDocLst ));
      // this.showMsgState = true;
      console.log('saveNER : success');
      this.ngOnInit();
      this.newtag=false;
      this.envInfo=[];//to show  empty record every time when we click Add new tag 

    }else{
      this.msgClr = 'red';
      this.msg = 'Could not Save!';
      console.warn('Could not save by api!');
      this.ngOnInit();
      this.newtag=false;
      this.envInfo=[]
    }
  }, err=> {
    this.msgClr = 'red';
    this.msg = 'Could not Save due to some Error! Try again later';
    console.error('Could not save!, : '+err);
  });

  this.showMsgState = true;


  


}
else{
  
  let tag_value: string;
  let modifiedState: boolean= false;
  // let tag_name: string;
  let index: number;
  let temp_lst: any=[];
  this.entDocLst.forEach(entDoc => {
    entDoc['description'].forEach(value => {
      if(typeof value != 'string'){
        modifiedState= true;
        temp_lst.push(value['value']);
      }else
        temp_lst.push(value);
    });
    entDoc['description']= temp_lst;
    temp_lst= [];
  });
  if(!modifiedState){
    this.entDocLst.forEach(entDoc=> {
      this.NERDocBkp.forEach(entDocBkp=> {
        if(entDoc['entity'] == entDocBkp['entity'])
          if(entDoc['description'].length != entDocBkp['description'].length)
            modifiedState= true;
      });
    });
  }
  console.log("entdoclst ",this.entDocLst)
  console.log("type entdoclst ",typeof(this.entDocLst))

  if(modifiedState){
    this.httpClient.put('/api/ner/saveNerTags/'+this.newtag, this.entDocLst, {'responseType': 'text'}).subscribe(data => {
      if(data == 'success'){
        this.msg = 'Saved successfully!';
        this.msgClr = 'green';
        this.NERDocBkp = JSON.parse(JSON.stringify( this.entDocLst ));
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
  }
}

  }
  setSaveChngState(){
    alert('--here--');
  }
  clearMsg(){
    this.showMsgState= false;
  }
}
