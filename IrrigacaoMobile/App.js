import * as React from 'react';
import { Button, View, ScrollView, SafeAreaView, RefreshControl , ToastAndroid, StyleSheet, Text } from 'react-native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { NavigationContainer } from '@react-navigation/native';
import RNPickerSelect from 'react-native-picker-select';
import DateTimePicker from '@react-native-community/datetimepicker';



const styles = StyleSheet.create({
  container: {
   flex: 1,
   paddingTop: 22
  },
  valve: {
    borderTopWidth:2
  },
  item: {
    padding: 10,
    fontSize: 18,
    height: 44,
  },
});


var ip = "192.168.0.20";
var configData = undefined
var listKeys = 0;

const ListItem = (props) => {
  return <View >
      <Text style={styles.item} >
      <Text style={{ fontWeight:"bold" }}>{props.label}:</Text>
      {props.value}</Text>
  </View>
}


class HomeScreen extends React.Component {

  constructor(props) {
      super(props);
      this.state = {
          data: [],
          refreshing: true,
      }
  }

  componentDidMount() {
      this.fetchConf();
  }

  fetchConf() {
      this.setState({ refreshing: true });
      fetch('http://'+ip+':8080/')
          .then(res => res.text())
          .then(resText => resText.replace(/'/g, '"'))
          .then(resJson => {
              console.log(resJson)
              configData = JSON.parse(resJson)
              this.setState({ data: configData });
              this.setState({ refreshing: false });
          }).catch(e => console.log(e));
  }

  handleRefresh = () => {
      this.setState({ refreshing: false }, () => { this.fetchConf() }); // call fetchCats after setting the state
  }


  render() {
  
    return (
      <SafeAreaView style={styles.container}>



        <ScrollView
          contentContainerStyle={styles.scrollView}
          refreshControl={
            <RefreshControl
              refreshing={this.state.refreshing}
              onRefresh={this.handleRefresh.bind(this)}
            />
          }>

            <ListItem key={listKeys++} label="Dia" value={this.state.data.last_day} ></ListItem>
            <ListItem key={listKeys++} label="Hora" value={this.state.data.current_time} ></ListItem>
            <ListItem key={listKeys++} label="Chuva hoje" value={this.state.data.precipitation_today} ></ListItem>
            <ListItem key={listKeys++} label="Chuva nas próximas horas" value={this.state.data.next_precipitation} ></ListItem>
            <ListItem key={listKeys++} label="Limite de chuva para ativação" value={this.state.data.precipitation_limit} ></ListItem>
            
            

            {this.state.data.valves != undefined &&
            this.state.data.valves.map(function(valve, i){
                return (
                      <View key={listKeys++} style={styles.valve}>

                      <ListItem label="Nome" value={valve.name} ></ListItem>
                      <ListItem label="Status" value={valve.irrigation} ></ListItem>
                      <ListItem label="Duração agendada" value={valve.duration} ></ListItem>
                      <ListItem label="Agendamento" value={valve.scheduled_time} ></ListItem>
                      <ListItem label="GPIO" value={valve.gpio} ></ListItem>
                      <ListItem label="Tempo que falta" value={valve.remains} ></ListItem>
                      <ListItem label="Tempo irrigado" value={valve.irrigated} ></ListItem>
                      
                      </View>
                      )
            })}

             
        </ScrollView>
      </SafeAreaView>)
  }
}


class IrrigacaoScreen extends React.Component {

    constructor(props) {
      super(props);
      this.state = {
        showTimer:false,
        date:new Date(2021,1,1,0,0,0),
        valve:0
      }
    }

  getItems(){
    if (configData == undefined){
      return []
    }
    valves = configData.valves
    items = []
    for (i = 0; i < valves.length; i++){
      item = {label:valves[i].name, value:i}
      items.push(item)
    }
    console.log(items);
    return items;
  }

  choiseTime(){
    this.setState({showTimer:true});
  }

  onChangeTimer(v){
    if (v.type == "set"){
      dt = v.nativeEvent.timestamp;
      console.log(dt);
      hour = dt.getHours()
      if (hour < 10){
        hour = "0"+hour
      }
      minute = dt.getMinutes()
      if (minute < 10){
        minute = "0"+minute
      }

      timer = hour+":"+minute+":00";
      fetch('http://'+ip+':8080/irrigate/'+this.state.valve+'/'+timer,{
            method:"PUT"
        })
        .then(res => res.text())
        .then(resText => JSON.parse(resText.replace(/'/g, '"')))
        .then(resJson => {
            if (resJson.status == true){
              ToastAndroid.show("Irrigação iniciada", ToastAndroid.SHORT);
            } else {
              ToastAndroid.show("Falha ao iniciar irrigação", ToastAndroid.SHORT);
            }
        }).catch(e => console.log(e));

    }
  }

  render(){
    items = this.getItems()

    return (
      <View style={{ flex: 1, alignItems: 'center'}}>

        <RNPickerSelect
            onValueChange={(value) => {this.setState({valve:value})} }
            items={items}
        />

        <Button onPress={this.choiseTime.bind(this)} title="Irrigar"></Button>

        {this.state.showTimer &&
        <DateTimePicker
                    testID="dateTimePicker"
                    value={this.state.date}
                    mode="time"
                    is24Hour={true}
                    display="spinner"
                    onChange={this.onChangeTimer.bind(this)}
                  />
        }

      </View>
    );
  }
}

const Drawer = createDrawerNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator initialRouteName="Home">
        <Drawer.Screen name="Home" component={HomeScreen} />
        <Drawer.Screen name="Irrigar" component={IrrigacaoScreen} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}