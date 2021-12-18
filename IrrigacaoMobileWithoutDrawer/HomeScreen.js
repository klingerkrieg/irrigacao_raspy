import * as React from 'react';
import { View, ScrollView, SafeAreaView, 
        RefreshControl, StyleSheet, Text, 
        TouchableHighlight, ToastAndroid} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
var data = require("./Data")

// yarn add react-navigation react-native-gesture-handler react-native-safe-area-context react-native-screens
// yarn add yarn add react-navigation-stack @react-native-community/masked-view @react-native-community/datetimepicker


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
      color:"gray",
    },
    cancel:{
        padding: 10,
        fontSize: 18,
        height: 44,
        color:'white',
        backgroundColor:'rgb(252, 146, 158);',
        borderColor:'white',
        borderWidth:1,
        borderRadius:40,
        textAlign:'center'
    },
    activate:{
        padding: 10,
        fontSize: 18,
        height: 44,
        color:'white',
        backgroundColor:'rgb(141, 200, 145);',
        borderColor:'white',
        borderWidth:1,
        borderRadius:40,
        textAlign:'center'
    },
  });


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
            showTimer:false,
            valveId:null,
            date:new Date(2021,1,1,0,0,0),
        }
    }
  
  
    fetchConf() {
        this.setState({ refreshing: true });
        fetch('http://'+data.IP+':8080/')
            .then(res => res.text())
            .then(resText => resText.replace(/'/g, '"'))
            .then(resJson => {
                console.log(resJson)
                //ToastAndroid.show(resJson, ToastAndroid.SHORT);
                data.configData = JSON.parse(resJson)
                this.setState({ data: data.configData });
                this.setState({ refreshing: false });
            }).catch(e => {
              console.log(e)
              ToastAndroid.show(e, ToastAndroid.SHORT);
            });
    }
  
    handleRefresh = () => {
        this.setState({ refreshing: false }, () => { this.fetchConf() }); // call fetchCats after setting the state
    }


    activateTimer(){
        this.interval = setInterval(() => { this.fetchConf() }, 20000);
    }

    componentDidMount() {
        this.fetchConf();
        this.activateTimer();
    }
    componentWillUnmount() {
        clearInterval(this.interval);
    }

    cancelarIrrigacao(valveId){
        this.setIrrigate(valveId,2,"Irrigação cancelada","Falha ao cancelar irrigação");
    }

    reativarIrrigacao(valveId){
        this.setIrrigate(valveId,1,"Irrigação reativada","Falha ao reativar irrigação");
    }

    interromperIrrigacao(valveId){
        this.setIrrigate(valveId,4,"Irrigação interrompida","Falha ao interromper irrigação");
    }
    

    setIrrigate(valveId, cod, msgOk, msgFail){
        var object = this;
        fetch('http://'+data.IP+':8080/set_irrigate/'+valveId+'/'+cod,{
            method:"PUT"
        })
        .then(res => res.text())
        .then(resText => JSON.parse(resText.replace(/'/g, '"')))
        .then(resJson => {
            if (resJson.status == true){
              ToastAndroid.show(msgOk, ToastAndroid.SHORT);
              object.fetchConf();
            } else {
              ToastAndroid.show(msgFail, ToastAndroid.SHORT);
            }
        }).catch(e => {ToastAndroid.show("Erro ao disparar comando", ToastAndroid.SHORT);});
    }


    setTimer(valveId){
        clearInterval(this.interval);
        this.setState({showTimer:true, valveId:valveId});
    }
    
    onChangeTimer(v){
        this.activateTimer();

        if (v.type == "set"){
          dt = v.nativeEvent.timestamp;
          
          hour = dt.getHours()
          if (hour < 10){
            hour = "0"+hour
          }
          minute = dt.getMinutes()
          if (minute < 10){
            minute = "0"+minute
          }

          var object = this;
    
          timer = hour+":"+minute+":00";

          url = 'http://'+data.IP+':8080/irrigate/'+this.state.valveId+'/'+timer
          fetch(url,{
                method:"PUT"
            })
            .then(res => res.text())
            .then(resText => JSON.parse(resText.replace(/'/g, '"')))
            .then(resJson => {
                object.setState({showTimer:false});
                if (resJson.status == true){
                  ToastAndroid.show("Irrigação iniciada", ToastAndroid.SHORT);
                  object.fetchConf();
                } else {
                  ToastAndroid.show("Falha ao iniciar irrigação", ToastAndroid.SHORT);
                }
            }).catch(e => {ToastAndroid.show("Erro ao iniciar irrigação", ToastAndroid.SHORT);});
    
          } else {
            this.setState({showTimer:false});
          }
    }
    

    renderValveItems(){
        var items = []
        valves = this.state.data.valves;
        if (valves == undefined){
            return []
        }
        for (var i = 0; i < valves.length; i++ ){
            valve = valves[i];
            items.push(
                <View key={listKeys++} style={styles.valve}>

                <ListItem label="Nome" value={valve.name} ></ListItem>
                <ListItem label="Status" value={valve.irrigation} ></ListItem>
                {valve.irrigation == "esperando" &&
                   <TouchableHighlight
                        activeOpacity={0.6}
                        underlayColor="#DDDDDD"
                        onPress={this.cancelarIrrigacao.bind(this,i)}>
                        <Text style={styles.cancel}>Cancelar irrigação de hoje</Text>
                  </TouchableHighlight>
                }
                {valve.irrigation == "irrigando" &&
                   <TouchableHighlight
                        activeOpacity={0.6}
                        underlayColor="#DDDDDD"
                        onPress={this.interromperIrrigacao.bind(this,i)}>
                        <Text style={styles.cancel}>Interromper irrigação</Text>
                  </TouchableHighlight>
                }
                {(valve.irrigation == "finalizado por hoje" 
                || valve.irrigation == "cancelado") &&
                   <TouchableHighlight
                        activeOpacity={0.6}
                        underlayColor="#DDDDDD"
                        onPress={this.reativarIrrigacao.bind(this,i)}>
                        <Text style={styles.activate}>Reativar irrigação de hoje</Text>
                  </TouchableHighlight>
                }
                <TouchableHighlight
                        activeOpacity={0.6}
                        underlayColor="#DDDDDD"
                        key={i}
                        onPress={this.setTimer.bind(this,i)}>
                        <Text style={styles.activate}>Irrigar agora</Text>
                </TouchableHighlight>
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


                <ListItem label="Duração agendada" value={valve.duration} ></ListItem>
                <ListItem label="Agendamento" value={valve.scheduled_time} ></ListItem>
                <ListItem label="GPIO" value={valve.gpio} ></ListItem>
                <ListItem label="Tempo que falta" value={valve.remains} ></ListItem>
                <ListItem label="Tempo irrigado" value={valve.irrigated} ></ListItem>
                
                </View>
                )
        }
        return items;
    }
  
  
    render() {

      var valveItems = this.renderValveItems();
    
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
              
              
  
              {valveItems}
  
               
          </ScrollView>
        </SafeAreaView>)
    }
  }

  export default HomeScreen;