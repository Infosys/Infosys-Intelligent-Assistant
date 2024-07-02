/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { MatTableDataSource, MatSort, MatPaginator, MatDialog } from '@angular/material';
import { KnowledgeInfoMappingModalComponent } from './knowledge-info-mapping-modal/knowledge-info-mapping-modal.component';


@Component({
    selector: 'app-knowledge-info',
    templateUrl: './knowledge-info.component.html',
    styleUrls: ['./knowledge-info.component.css']
})

export class knowledgeInfoComponent{


    @ViewChild('knowledgeInfoFile') fileInput: ElementRef;
    @ViewChild(MatSort) sort: MatSort;
    @ViewChild(MatPaginator) paginator: MatPaginator;
    dataSource;
    displayedColumns = [];
    loader: boolean;
    hasKnowledgeInfoData: boolean;
    knowledgeInfoLst: any = []; 
    hasApplicationDetails: boolean = false;
  columnNames: any[];
  //sort: any;

    constructor(private httpclient: HttpClient, public dialog: MatDialog, 
      private router: Router){
      this.getKnowledgeInfo();
    }

    getKnowledgeInfo(){
      this.httpclient.get('/api/ner/getKnowledgeInfo').subscribe(data => {
        if(data['response'] != 'failure'){
          this.knowledgeInfoLst = data['response'];
          this.createTable();
          this.hasKnowledgeInfoData = true;
        }else {
          this.hasKnowledgeInfoData = false;
          console.error('Could not get knowledge data! error in the api');
        }
      },err => {
        console.error('Could not get knowledge data! '+err);
      });
    }

    createTable() {
      this.displayedColumns = Object.keys(this.knowledgeInfoLst[0]);
      // this.displayedColumns = this.columnNames.map(x => x.id);
      let tableArr: Element[] = this.knowledgeInfoLst;
      this.dataSource = new MatTableDataSource(tableArr);
       this.dataSource.sort = this.sort;
       this.dataSource.paginator = this.paginator;
    }
    
    uploadKnowledgeInfoFile(){
      console.log('in upload application details...')
      const fileBrowser = this.fileInput.nativeElement;

      if (fileBrowser.files && fileBrowser.files[0]) {
        let dataToModal = {};
        let file = fileBrowser.files[0];
        const formData = new FormData();
        formData.append('knowledgeInfoDetails', fileBrowser.files[0]);

        this.httpclient.post('/api/ner/getKnowledgeInfoColumnNames', formData, {responseType: 'json'}).subscribe(data => {
          if (data['response'] != 'failure') {
            dataToModal['file'] = file;
            dataToModal['accountColumnsLst'] = data['response']['account_column_headers'];
            dataToModal['iiaColumnsLst'] = data['response']['iia_column_headers'];
            let dialogRef = this.dialog.open( KnowledgeInfoMappingModalComponent, {
              data: dataToModal,
              height: '100%',
              width: '650px'
            });
            dialogRef.afterClosed().subscribe(() => { this.getKnowledgeInfo(); });
          } else
          console.log('Oops!!, No any data received');
        });
      }else{
        alert('Please choose the right file..!');
      }
    }

    deleteKGInfodetails () {
      if (this.knowledgeInfoLst.length > 0) {
        let confirmState = confirm('You have choosen to delete all Information!');
        if (confirmState)
        this.httpclient.delete('/api/ner/deleteKGInfoDetails', {responseType: 'text'}).subscribe(response => {
          console.log(response);
          this.knowledgeInfoLst = [];
          this.hasKnowledgeInfoData = false;
          // this.getKnowledgeInfo();
        }, err => {
          console.error(err);
        });
      } else
      alert('There are no Records to Delete!');
    }

}