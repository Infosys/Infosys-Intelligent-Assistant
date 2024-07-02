/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Sort } from '@angular/material';
import { Component } from '@angular/core';
import { DataSource } from '@angular/cdk/collections';
import { Observable, of } from 'rxjs';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { OnInit } from '@angular/core';
export interface IncidentTickets {
  number: string;
  category: string;
  priority: string;
  description: string;
  state: string;
}
export interface ResourceInfo {
  id: number;
  name: string;
  tickets_assigned: number;
  workload: number;
  availability: boolean;
  available_till: string;
  next_available_in: string;
  incidentsLst: IncidentTickets[];
  // incidentsLst: MatTableDataSource<IncidentTickets>;
}
var ELEMENT_DATA: ResourceInfo[];
@Component({
  selector: 'app-validation-message',
  templateUrl: './validation-message.component.html',
  styleUrls: ['./validation-message.component.css'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({ height: '0px', minHeight: '0', visibility: 'hidden' })),
      state('expanded', style({ height: '*', visibility: 'visible' })),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ]),
  ],
})
export class ValidationMessageComponent implements OnInit {
  dataSource: CreateDataSource;
  showDetailsOf: string;
  failedRoasterUploadDetails: any = {};
  resourcesOfGroupInfo: any = {};
  approvedTickets: any = [];
  assignGroup: string;
  columnsToDisplay = ['name', 'tickets_assigned', 'workload', 'availability', 'available_till', 'next_available_in'];
  incidentColms = ['number', 'description', 'state'];
  public incidentConverter: IncidentTickets[] = [];
  public elementData: ResourceInfo[] = [];
  isExpansionDetailRow = (i: number, row: Object) => row.hasOwnProperty('detailRow');
  expandedElement: any;
  constructor(public activeModal: NgbActiveModal) { }
  ngOnInit() {
    if (this.failedRoasterUploadDetails != undefined)
      this.showDetailsOf = (Object.keys(this.failedRoasterUploadDetails).length > 0) ? 'roasterDetails' : 'ticketDetials';
    else {
      this.showDetailsOf = 'resourceWorkloadInfo';
      let count = 0;
      for (let resourceDoc of this.resourcesOfGroupInfo) {
        this.incidentConverter = [];
        for (let incidentDoc of resourceDoc['incidentsLst']) {
          this.incidentConverter.push({
            number: incidentDoc['number'], category: incidentDoc['category'], priority: incidentDoc['priority'], description: incidentDoc['description'], state: incidentDoc['state']
          });
        }
        this.elementData.push({
          id: count += 1,
          name: resourceDoc['name'],
          tickets_assigned: resourceDoc['tickets_assigned'],
          workload: resourceDoc['workload'],
          availability: resourceDoc['availability'],
          available_till: resourceDoc['available_till'],
          next_available_in: resourceDoc['next_available_in'],
          incidentsLst: this.incidentConverter
          // incidentsLst: new MatTableDataSource( this.incidentConverter )
        });
      }
      ELEMENT_DATA = this.elementData;
      this.dataSource = new CreateDataSource();
    }
  }
  sortResourceInfo(sort: Sort) {
    if (sort.direction == '') { sort.active = 'id'; sort.direction = 'asc'; }
    ELEMENT_DATA.sort((r1, r2) => this.sortResourceInfoOf(r1, r2, sort))
    this.dataSource = new CreateDataSource;
  }
  sortResourceInfoOf(r1, r2, sort: Sort) {
    const one = sort.direction === 'asc' ? 1 : (sort.direction === 'desc' ? -1 : 0);
    if (r1[sort.active] > r2[sort.active])
      return one;
    else if (r1[sort.active] < r2[sort.active])
      return -one;
    else
      return 0;
  }
}
/**
 * Data source to provide what data should be rendered in the table. The observable provided
 * in connect should emit exactly the data that should be rendered by the table. If the data is
 * altered, the observable should emit that new set of data on the stream. In our case here,
 * we return a stream that contains only one set of data that doesn't change.
 */
export class CreateDataSource extends DataSource<any> {
  /** Connect function called by the table to retrieve one stream containing the data to render. */
  connect(): Observable<ResourceInfo[]> {
    const rows = [];
    ELEMENT_DATA.forEach(element => rows.push(element, { detailRow: true, element }));
    return of(rows);
  }
  disconnect() { }
}
