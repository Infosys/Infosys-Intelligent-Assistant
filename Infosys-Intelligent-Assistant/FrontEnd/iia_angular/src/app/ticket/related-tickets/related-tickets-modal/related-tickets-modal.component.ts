/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import  { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
@Component({ 
    selector: 'related-tickets-modal', 
    templateUrl: './related-tickets-modal.component.html'
})
export class RelatedTicketsModalComponent {
    constructor( @Inject( MAT_DIALOG_DATA ) public data: any ) { }
    state = this.data.state;
    keys = this.data.keys;
    dataToDisplay = this.data.dataToDisplay;
}