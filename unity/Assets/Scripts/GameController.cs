using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.IO;

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

    void Awake()
    {
        StartCoroutine(GetInitialSettings());
    }

    IEnumerator GetInitialSettings()
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
        ServerResponse response = JsonUtility.FromJson<ServerResponse>(jsonResponse);

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

        for (int j = 0; j < numberOfElevators; j++)
        {
            Floor[] floors = new Floor[numberOfFloors + 1];
            Vector3 startingPosition = this.transform.position;

            for (int i = 0; i < numberOfFloors + 1; i++)
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
            elevatorsController[j].floors = floors; // Ensure that ElevatorController has a public 'floors' field
        }
    }
}
