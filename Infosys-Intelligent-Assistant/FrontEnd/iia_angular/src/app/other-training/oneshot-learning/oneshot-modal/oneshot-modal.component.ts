/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import {Component, ViewChild,ElementRef,Inject} from '@angular/core';
import { MAT_DIALOG_DATA,MatDialogRef } from '@angular/material/dialog';


@Component({
    selector: 'app-oneshot-modal',
    templateUrl: './oneshot-modal.component.html',
    styleUrls: ['./oneshot-modal.component.css']
})

export class OneShotModalComponent   {
    constructor( @Inject( MAT_DIALOG_DATA ) public data: any ,public dialogRef:MatDialogRef<OneShotModalComponent>) { }

    
    onNoClick():void{
        this.dialogRef.close();
        
    }

}