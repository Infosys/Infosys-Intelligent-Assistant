/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
@Component({
  selector: 'app-imageoneshot-modal',
  templateUrl: './imageoneshot-modal.component.html',
  styleUrls: ['./imageoneshot-modal.component.css']
})
export class ImageOneShotModalComponent implements OnInit {
  constructor(@Inject(MAT_DIALOG_DATA) public data: any, public dialogRef: MatDialogRef<ImageOneShotModalComponent>, private httpclient: HttpClient) { }
  columnsSelected: any = [];
  columnNames: any = [];
  ngOnInit() {
    this.httpclient.get('/api/imageAnalysis/getColumnNames').subscribe(data => {
      if (data['response'] != 'failure') {
        this.columnsSelected = data['response'];
        this.columnNames = this.columnsSelected
      } else {
        console.warn('Could not get data from api!');
      }
    }, err => {
      console.error('Could not get data! ,' + err)
    });
    for (let i = 0; i < this.columnNames.length; i++) {
      this.data_to_send[this.columnNames[i]] = '';
    }
  }
  data_to_send = {};
  img_name: string;
  error_details: string;
  image_trained_state: boolean = false;
  uploadImage_and_Train() {
    this.data_to_send['incident_number'] = this.data.incident_no;
    this.data_to_send['image_name'] = this.img_name;
    this.data_to_send['error_details'] = this.error_details;
    this.httpclient.post('/api/newimage/savevector', this.data_to_send, { responseType: 'text' })
      .subscribe(data => {
        if (data == "success") {
          this.image_trained_state = true;
          this.dialogRef.close(this.image_trained_state);
        } else {
          alert('Some issue occured while training this image  ,please check again ')
          this.dialogRef.close(this.image_trained_state);
        }
      });
  }
  onNoClick(): void {
    this.dialogRef.close();
  }
}