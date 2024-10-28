import {
    fixedHeaders,
    fixedRowsText,
    ColumnIndices,
    RowIndices,
    lenFixedRowsText,
    lenFixedHeaders,
    borderStyle,
    requiredProperties,
} from './constants.js';

fetch('/assignment/load_data')
    .then(response => response.json())
    .then(loadData => {
        const {
            courses,
            users,
            teachers,
            researchers,
            supervisors,
            preferences,
            organizations,
            current_year,
            saved_data,
            comments,
            MAX_LOAD
        } = loadData;
        courses.forEach(course => {
            let teachersId = Object.values(teachers).filter(teacher => teacher.course_id === course.id);
            let teachersName = teachersId.map(teacher => {
                let teacherUser = users[teacher.user_id];
                return teacherUser ? `${teacherUser.name} ${teacherUser.first_name}` : '';
            });
            course.assigned_teachers = teachersName.join(', ');
        });

        //Split long text in the course header
        const coursesHeaders = courses.map(course => {
            const maxLength = 30;
            const courseName = course.title;

            if (courseName.length > maxLength) {
                const firstLine = courseName.substring(0, maxLength / 2);
                const secondLine = courseName.substring(maxLength / 2);
                const finalResult = `${secondLine}<br>${firstLine}<br>${course.code}`;
                return finalResult
            } else {
                const finalResult = `${courseName}<br>${course.code}`;
                return finalResult;
            }
        });

        //Create all course header
        const allHeaders = fixedHeaders.concat(coursesHeaders);

        function fixedRowsData() {
            let rows = [];

            const allProperties = Object.keys(courses[0]);
            const properties = allProperties.filter(prop => requiredProperties.includes(prop));
            // Use to keep the order of the properties
            const orderedProperties = requiredProperties.map(prop => properties.includes(prop) ? prop : null).filter(prop => prop !== null);
            orderedProperties.push('tutors')

            for (let i = 0; i < lenFixedRowsText; i++) {
                let row = {
                    researchers: {
                        id: "",
                        name: ""
                    },
                    org: "",
                    promoter: "",
                    totalLoad: "",
                    loadQ1: "",
                    loadQ2: ""
                };

                courses.forEach(course => {
                    row[course.id] = orderedProperties.includes('tutors') && orderedProperties[i] === 'tutors' ? 0 : course[orderedProperties[i]];
                });
                rows.push(row);
            }

            return rows;
        }

        function buildRow(user, isFilled) {
            const row = {};
            row.researchers = {
                id: user.id,
                name: isFilled ? `${user.name} ${user.first_name}` : ""
            };
            return row;
        }

        function userRowsData(clearData=false) {
            const rows = [];

            for (const researcherId in researchers) {
                const researcher = researchers[researcherId];
                const user = users[researcher.user_id];
                //The first line displays the preferences for each user
                const preferenceRow = buildRow(user, true);
                //The second line allows admins to assign a course to the user
                const AssignmentRow = buildRow(user, false);
                const assistantOrg = organizations[user.organization_id];

                let researcherSupervisor = Object.values(supervisors).filter(supervisor => supervisor.researcher_id === researcher.id);
                let supervisorNames = researcherSupervisor.map(supervisor => {
                    let user = users[supervisor.supervisor_id];
                    return user ? `${user.name}` : '';
                });
                researcher.promoters = supervisorNames.join(', ');

                preferenceRow.org = assistantOrg ? assistantOrg.name : "";
                preferenceRow.promoter = researcher.promoters;
                preferenceRow.totalLoad = researcher.max_loads;
                preferenceRow.loadQ1 = 0;
                preferenceRow.loadQ2 = 0;

                //This line is only used to store course assignments, so the other values are empty.
                const emptyKeys = ['org', 'promoter', 'totalLoad', 'loadQ1', 'loadQ2'];
                emptyKeys.forEach(key => {
                    AssignmentRow[key] = "";
                });

                const userPrefs = Object.values(preferences).filter(pref => pref.researcher_id === researcher.id);

                let pos = 1;
                courses.forEach(course => {
                    const isPref = userPrefs.find(pref => pref.course_id === course.id);
                    const savedAssignment = saved_data && !clearData ? saved_data.find(data => data.user_id === user.id && data.course_id === course.id) : null;
                    const code = course.id;
                    preferenceRow[code] = isPref ? pos++ : "";
                    AssignmentRow[code] = savedAssignment ? savedAssignment.position : "";
                });

                rows.push(preferenceRow);
                rows.push(AssignmentRow);
            }
            return rows;
        }

        const fixedRows = fixedRowsData();
        const userRows = userRowsData();


        function getCourseColumns() {
            const fixedColumns = [
                {data: 'researchers.id'},
                {data: 'researchers.name'},
                {data: 'org'},
                {data: 'promoter'},
                {data: 'totalLoad'},
                {data: 'loadQ1'},
                {data: 'loadQ2'}
            ];

            courses.forEach(course => {
                const code = course.id;
                let col = {data: code};
                fixedColumns.push(col)
            });
            return fixedColumns;
        }

        const columns = getCourseColumns();

        let data = fixedRows.concat(userRows);
        let savedComments = comments ? comments : [];

        const nbrLines = data.length - 1;
        const nbrCols = columns.length - 1;

        const mergeCellsSettings = [];
        for (let row = lenFixedRowsText; row < nbrLines; row += 2) {
            for (let col = 1; col <= lenFixedHeaders - 1; col++) {
                mergeCellsSettings.push({
                    row: row,
                    col: col,
                    rowspan: 2,
                    colspan: 1
                });
            }
        }

        const table = new Handsontable(document.getElementById("handsontable"), {
            data: data,
            fixedColumnsLeft: lenFixedHeaders,
            fixedRowsTop: lenFixedRowsText,
            manualColumnMove: true,
            manualColumnResize: true,
            manualRowResize: true,
            mergeCells: mergeCellsSettings,
            hiddenColumns: {
                columns: [0],
                indicators: true,
            },
            hiddenRows: {
                rows: [0],
                indicators: true,
            },
            contextMenu: ['commentsAddEdit', 'commentsRemove', 'hidden_columns_hide', 'hidden_rows_hide', 'hidden_columns_show', 'hidden_rows_show'],
            comments: true,
            filters: true,
            dropdownMenu: ['filter_by_value', 'filter_action_bar', 'undo'],
            className: 'controlsQuickFilter htCenter htMiddle',
            colHeaders: allHeaders,
            columns: columns,
            colWidths: 100,
            columnHeaderHeight: 225,
            rowHeaders: fixedRowsText,
            rowHeaderWidth: 125,
            // Disable the cells that contain user preferences
            cells: function (row, col) {
                const cellProperties = {};
                if (row >= lenFixedRowsText && col >= lenFixedHeaders && row % 2 === 0) {
                    cellProperties.readOnly = true;
                }
                return cellProperties;
            },
            afterInit: function () {
                if (savedComments) {
                    savedComments.forEach(comment => {
                        const commentsPlugin = this.getPlugin('comments');
                        commentsPlugin.setCommentAtCell(comment.row, comment.column, comment.value);
                    });
                }
            },
            afterGetColHeader: function (col, th) {
                th.style.transform = 'rotate(180deg)';
                th.style.writingMode = 'vertical-lr';
                th.style.textAlign = 'center';
                th.style.fontWeight = 'bold';
                th.style.height = '100px';
                th.style.lineHeight = '100px';

                if (col > lenFixedHeaders - 1) {
                    let colData = this.getDataAtCol(col);
                    if (colData[RowIndices.TOTAL_ASSISTANT_NOW] >= colData[RowIndices.ASSISTANTS]) {
                        th.style.backgroundColor = 'green';
                    }
                }
            },
            afterChange: function (changes) {
                if (changes) {
                    changes.forEach(([row, prop, oldValue, newValue]) => {
                        let col = this.propToCol(prop);
                        if ((col >= lenFixedHeaders && row >= lenFixedRowsText) && (row % 2 === 1)) {

                            const colInfos = this.getDataAtProp(prop);
                            let nbrAssistants = colInfos[RowIndices.TOTAL_ASSISTANT_NOW];
                            const rowInfos = this.getDataAtRow(row - 1);
                            const quadri = colInfos[RowIndices.QUADRI];

                            let loadKey = quadri === 1 ? ColumnIndices.LOAD_Q1 : ColumnIndices.LOAD_Q2;
                            let loadValue = rowInfos[loadKey];

                            // Old non-empty value and new empty value: loadValue-- and nbrAssistants--.
                            // Old non-empty value and new non-empty value: loadValue++ and nbrAssistants++.
                            // Old null value and new non-empty value: loadValue++ and nbrAssistants++.
                            // Old non-null value and new null value: loadValue-- and nbrAssistants--.
                            if (oldValue !== newValue) {
                                if ((oldValue !== '' && newValue === '') || (oldValue !== null && newValue === null)) {
                                    if (loadValue > 0 && nbrAssistants > 0) {
                                        loadValue--;
                                        nbrAssistants--;
                                    }
                                } else if ((oldValue === '' && newValue !== '') || (oldValue === null && newValue !== null)) {
                                    loadValue++;
                                    nbrAssistants++;
                                }
                                this.setDataAtCell(row - 1, loadKey, loadValue);
                                this.setDataAtCell(RowIndices.TOTAL_ASSISTANT_NOW, col, nbrAssistants);
                            }
                        }
                    });
                }
            },
            afterSetCellMeta: function (row, col, key, value) {
                if (key === 'comment') {
                    savedComments = value === undefined
                        ? savedComments.filter(comment => comment.row !== row || comment.column !== col)
                        : [...savedComments.filter(comment => comment.row !== row || comment.column !== col), {
                            'row': row,
                            'column': col,
                            'key': key,
                            'value': value.value
                        }];
                }
            },
            afterRenderer: function (TD, row, col, prop, value, cellProperties) {
                if ((col >= lenFixedHeaders && row >= lenFixedRowsText) && (row % 2 === 1) && (value !== '')) {
                    TD.style.fontWeight = 'bold'; // Bold text
                    TD.style.textAlign = 'left'; // Left alignment
                }
                //Style first col if needed
                if (col === 0 && row < lenFixedRowsText) {
                    TD.style.fontWeight = 'bold';
                    TD.style.textAlign = 'left';
                }
                //(row%2) === 1 to avoid empty lines
                if (row >= lenFixedRowsText && (row % 2) === 0 && col < lenFixedHeaders) {
                    const rowValue = this.getDataAtRow(row);
                    if (col === ColumnIndices.LOAD_Q1 || col === ColumnIndices.LOAD_Q2) {
                        const total_load = rowValue[ColumnIndices.TOTAL_LOAD];
                        const load_q1 = rowValue[ColumnIndices.LOAD_Q1];
                        const load_q2 = rowValue[ColumnIndices.LOAD_Q2];

                        //First case: load Q1 + Q2 = total load
                        //Second case: load Q1 or Q2 = half of total load
                        if (load_q1 + load_q2 > total_load) {
                            TD.style.backgroundColor = 'red';
                        } else if ((total_load === MAX_LOAD['Teaching assistant'] || total_load === MAX_LOAD["Phd"]) && (total_load / value <= MAX_LOAD["Phd"] || load_q1 + load_q2 === total_load)) {
                            TD.style.backgroundColor = 'green';
                        } else if (total_load === MAX_LOAD["Postdoc"]) {
                            if (value === MAX_LOAD["Postdoc"]) {
                                TD.style.backgroundColor = 'green';
                            } else {
                                if ((load_q1 === MAX_LOAD["Postdoc"] && load_q2 === 0) || (load_q1 === 0 && load_q2 === MAX_LOAD["Postdoc"])) {
                                    TD.style.backgroundColor = 'green';
                                }
                            }
                        }
                    }
                }
            },
            customBorders: [
                {
                    range: {
                        from: {row: 0, col: 0},
                        to: {row: nbrLines, col: 6}
                    },
                    end: borderStyle,
                },
                {
                    range: {
                        from: {row: 0, col: 0},
                        to: {row: 5, col: nbrCols}
                    },
                    bottom: borderStyle,
                },
                {
                    row: 5,
                    col: 6,
                    bottom: borderStyle
                },
            ],
            beforeFilter(conditionsStack) {
                const filtersPlugin = this.getPlugin('filters');
                //Get the user data without the fixed rows
                const tab = this.getData().slice(lenFixedRowsText);

                let values = [];
                const filteredResults = [];
                //Get the number of the column to filter

                if (conditionsStack && conditionsStack.length > 0) {
                    const col = conditionsStack[0].column;

                    if (conditionsStack && conditionsStack.length > 0) {
                        for (let i = 0; i < conditionsStack.length; i++) {
                            //Get the matching values to filter
                            values = conditionsStack[i].conditions[0].args.flat();

                            //Verify if the row value for the specific column is in the filter
                            for (const row of tab) {
                                if (values.includes(row[col])) {
                                    //Push id to the filteredResults array
                                    filteredResults.push(row[0]);
                                }
                            }
                        }
                    }
                    filtersPlugin.clearConditions();
                    //Create a new condition to filter the data based on the id
                    filtersPlugin.addCondition(0, 'by_value', [filteredResults]);
                }
            },
            afterFilter(conditionsStack) {
                const filtersPlugin = this.getPlugin('filters');
                const filtersRowsMap = filtersPlugin.filtersRowsMap;

                // Exclude fixed lines from the filter
                for (let i = 0; i < lenFixedRowsText; i++) {
                    filtersRowsMap.setValueAtIndex(i, false);
                }
            },
            licenseKey: "non-commercial-and-evaluation",
        });

        $(document).ready(function () {
            function updateToastContent(message) {
                let toastBody = document.querySelector('#toast-notification .toast-body');
                toastBody.textContent = message;
            }

            let toastNotification = new bootstrap.Toast(document.getElementById('toast-notification'));

            $('#button-export').click(function () {
                const exportPlugin = table.getPlugin('exportFile');
                exportPlugin.downloadFile('csv', {
                    bom: false,
                    columnDelimiter: ',',
                    columnHeaders: true,
                    exportHiddenColumns: false,
                    exportHiddenRows: false,
                    fileExtension: 'csv',
                    filename: 'ICTM-CSV-file_[YYYY]-[MM]-[DD]',
                    mimeType: 'text/csv',
                    rowDelimiter: '\r\n',
                    rowHeaders: true
                });
                updateToastContent('Data exported to CSV');
                toastNotification.show();
            });

            async function saveAssignment(isDraft = false) {
                const slicedData = data.slice(lenFixedRowsText);
                const savedData = [];

                for (let i = 0; i < slicedData.length; i += 2) {
                    const user_row = slicedData[i];
                    const course_row = slicedData[i + 1];

                    const userData = {
                        user_id: user_row.researchers.id,
                        load_q1: user_row.loadQ1,
                        load_q2: user_row.loadQ2,
                    };

                    const courseData = {};
                    courses.forEach(course => {
                        if (course_row[course.id] !== '') {
                            courseData[course.id] = course_row[course.id];
                        }
                    });
                    savedData.push({userData, courseData})
                }

                const tableData = {
                    data: savedData,
                    comments: savedComments,
                    isDraft: isDraft
                };

                try {
                    const response = await fetch('/assignment/publish_assignments', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(tableData),
                    });

                    if (response.ok) {
                        updateToastContent('Assignments published');
                        toastNotification.show();
                    } else {
                        updateToastContent('Failed to publish assignments' + response.statusText);
                        toastNotification.show();
                    }
                } catch (error) {
                    updateToastContent('Error: ' + error);
                    toastNotification.show();
                }
            }

            $('#button-create-assignments').click(async function () {
                await saveAssignment(true);
            });

            $('#button-clear-assignments').click(function () {
                savedComments = [];
                const newUsersRow = userRowsData(true);
                data = fixedRows.concat(newUsersRow);
                table.loadData(data);
                updateToastContent('Data cleared');
                toastNotification.show();
            });

            $('#button-publish-assignments').click(async function () {
                await saveAssignment();
            });
        });
    });

