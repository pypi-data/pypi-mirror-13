import QtQuick 2.0
import QtQuick.Controls 1.3

GroupBox {
    id: root
    property var model: null

    SystemPalette { id: sysPalette; colorGroup: SystemPalette.Active }

    ScrollView {
        anchors.fill: parent
        verticalScrollBarPolicy: Qt.ScrollBarAlwaysOn

        ListView {
            anchors.fill: parent

            model: root.model
            spacing: 5

            Rectangle {
                anchors.fill: parent
                color: sysPalette.base
                z: -1
            }

            delegate: CheckBox {
                id: box
                text: model.name
                Component.onCompleted: checkedState = model.checkState
                onClicked: {
                    model.checkState = checkedState
                }
                Connections {
                    target: root.model
                    onDataChanged: {
                        box.checkedState = model.checkState
                    }
                }
            }
        }
    }
}
