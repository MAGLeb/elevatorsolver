using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.IO;
using Newtonsoft.Json;

[System.Serializable]
public class ServerResponse
{
    public int[] action;
    public int[] outside_calls;
    public int[][] elevators_state;
}

[System.Serializable]
public class SettingsResponse
{
    public int elevators;
    public int levels;
}

public class GameController : MonoBehaviour
{
    public ElevatorController[] elevatorsController;
    public string serverURL = "http://localhost:5000";
    public float requestInterval = 0.5f;
    private float timeSinceLastRequest = 0f;
    private float levelSize = 1f;

    void Awake()
    {
        StartCoroutine(GetInitialSettings());
    }

    private IEnumerator GetInitialSettings()
    {
        UnityWebRequest request = UnityWebRequest.Get(serverURL + "/get_settings");
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Server request failed: " + request.error);
        }
        else
        {
            SettingsResponse settings = JsonUtility.FromJson<SettingsResponse>(request.downloadHandler.text);
            CreateElevators(settings.elevators, settings.levels);
        }
    }

    void Update()
    {
        timeSinceLastRequest += Time.deltaTime;

        if (timeSinceLastRequest >= requestInterval)
        {
            timeSinceLastRequest = 0f;
            RequestElevatorAction();
        }
    }

    public void RequestElevatorAction()
    {
        StartCoroutine(GetActionFromServer());
    }

    private IEnumerator GetActionFromServer()
    {
        UnityWebRequest request = UnityWebRequest.Get(serverURL + "/get_action");
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Server request failed: " + request.error);
        }
        else
        {
            HandleServerResponse(request.downloadHandler.text);
        }
    }

    private void HandleServerResponse(string jsonResponse)
    {
        ServerResponse response = JsonConvert.DeserializeObject<ServerResponse>(jsonResponse);

        for (int j = 0; j < response.action.Length; j++)
        {
            for (int i = 0; i < response.outside_calls.Length; i++)
            {
                if (response.outside_calls[i] == 1 && response.elevators_state[j][i] == 1)
                {
                    elevatorsController[j].floors[i].State = FloorState.CalledFromBoth;
                }
                else if (response.outside_calls[i] == 1)
                {
                    elevatorsController[j].floors[i].State = FloorState.CalledFromOutside;
                }
                else if (response.elevators_state[j][i] == 1)
                {
                    elevatorsController[j].floors[i].State = FloorState.CalledFromInside;
                }
                else
                {
                    elevatorsController[j].floors[i].State = FloorState.None;
                }
            }
            elevatorsController[j].PerformAction(response.action[j]);
        }
    }

    void CreateElevators(int numberOfElevators, int numberOfFloors)
    {
        elevatorsController = new ElevatorController[numberOfElevators];

        // Определение начальной позиции первого лифта
        Vector3 startingPosition = this.transform.position;

        for (int j = 0; j < numberOfElevators; j++)
        {
            GameObject elevatorObject = new GameObject("Elevator " + j);
            elevatorObject.transform.position = startingPosition + new Vector3(0, 0, j * (levelSize * 2 + 4.0f));

            GameObject elevatorCabin = GameObject.CreatePrimitive(PrimitiveType.Cube);
            elevatorCabin.name = "Elevator cabin";
            elevatorCabin.transform.parent = elevatorObject.transform;
            elevatorCabin.transform.localPosition = Vector3.zero;
            elevatorCabin.transform.localScale = new Vector3(levelSize / 2, levelSize, levelSize);
            ElevatorController elevator = elevatorCabin.AddComponent<ElevatorController>();

            SetupDoors(elevator);

            elevator.floors = CreateFloors(numberOfFloors);
            for (int i = 0; i < elevator.floors.Length; i++)
            {
                elevator.floors[i].transform.parent = elevatorObject.transform;
                elevator.floors[i].transform.localPosition = new Vector3(0, i + (i * 0.1f), 1.5f + levelSize);
            }

            elevatorsController[j] = elevator;
        }
    }

    void SetupDoors(ElevatorController elevator)
    {
        Material doorMaterial = new Material(Shader.Find("Standard"));
        doorMaterial.color = new Color(0.44f, 0.26f, 0.08f);  // Коричневый цвет

        float doorWidth = levelSize / 2 - 0.025f;
        GameObject leftDoor = GameObject.CreatePrimitive(PrimitiveType.Cube);
        leftDoor.name = "Left door";
        leftDoor.transform.parent = elevator.transform;
        leftDoor.transform.localScale = new Vector3(0.05f, levelSize, doorWidth);
        leftDoor.transform.localPosition = new Vector3(-levelSize / 2, 0, 0.25f);

        GameObject rightDoor = GameObject.CreatePrimitive(PrimitiveType.Cube);
        rightDoor.name = "Right door";
        rightDoor.transform.parent = elevator.transform;
        rightDoor.transform.localScale = new Vector3(0.05f, levelSize, doorWidth);
        rightDoor.transform.localPosition = new Vector3(-levelSize / 2, 0, -0.25f);

        leftDoor.GetComponent<Renderer>().material = doorMaterial;
        rightDoor.GetComponent<Renderer>().material = doorMaterial;

        elevator.leftDoor = leftDoor.transform;
        elevator.rightDoor = rightDoor.transform;
    }


    private Floor[] CreateFloors(int numberOfFloors)
    {
        Floor[] floors = new Floor[numberOfFloors];
        Vector3 startingPosition = this.transform.position;

        for (int i = 0; i < numberOfFloors; i++)
        {
            GameObject newFloorObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            newFloorObject.name = "Floor " + (i);
            newFloorObject.transform.parent = this.transform;
            newFloorObject.transform.position = startingPosition + new Vector3(0, i + (i * 0.1f), 0);

            Floor floor = newFloorObject.AddComponent<Floor>();
            floor.Initialize(i, newFloorObject.transform, newFloorObject.GetComponent<MeshRenderer>());

            floors[i] = floor;

            // Creating 3D text and assigning it to the floor
            GameObject textObj = new GameObject("FloorNumberText");
            textObj.transform.parent = newFloorObject.transform;
            float zShift = i >= 10 ? 0.3f : 0.15f;
            textObj.transform.localPosition = new Vector3(-0.6f, 0.4f, zShift);
            textObj.transform.localEulerAngles = new Vector3(0, 90, 0);
            textObj.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f);

            TextMesh textMesh = textObj.AddComponent<TextMesh>();
            textMesh.text = i.ToString();
            textMesh.fontSize = 12;
            textMesh.color = Color.black;

            floor.textMesh = textMesh;
        }
        return floors;
    }
}
