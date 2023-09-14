using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.IO;

[System.Serializable]
public class ServerResponse
{
    public int action;
    public int[] outside_calls;
    public int[] inside_calls;
}

public class GameController : MonoBehaviour
{
    public int numberOfFloors = 10;
    public Floor[] floors;
    public ElevatorController elevatorController;
    public string serverURL = "http://localhost:5000/get_action";
    public float requestInterval = 0.1f;
    private float timeSinceLastRequest = 0f;

    void Awake()
    {
        CreateFloors();
		elevatorController.Floors = floors;
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
        UnityWebRequest request = UnityWebRequest.Get(serverURL);
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

        for (int i = 0; i < response.outside_calls.Length; i++)
        {
			if (response.outside_calls[i] == 1 && response.inside_calls[i] == 1) 
			{
				floors[i].State = FloorState.CalledFromBoth;
			} 
			else if (response.outside_calls[i] == 1) 
			{
				floors[i].State = FloorState.CalledFromOutside;
			} 
			else if (response.inside_calls[i] == 1)
			{
				floors[i].State = FloorState.CalledFromInside;
			}
			else
			{
				floors[i].State = FloorState.None;
			}
        }
        elevatorController.PerformAction(response.action);
    }

 	void CreateFloors()
    {
        floors = new Floor[numberOfFloors + 1];
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

        	// Создаем 3D текст и присваиваем его этажу
   			GameObject textObj = new GameObject("FloorNumberText");
    		textObj.transform.parent = newFloorObject.transform;
			float zShift = i >= 10 ? 0.3f : 0.15f;
    		textObj.transform.localPosition = new Vector3(-0.6f, 0.4f, zShift); 
    		textObj.transform.localEulerAngles = new Vector3(0, 90, 0); 
			textObj.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f); 

    		TextMesh textMesh = textObj.AddComponent<TextMesh>();
    		textMesh.text = (i).ToString();
    		textMesh.fontSize = 12;
    		textMesh.color = Color.black;

    		floor.textMesh = textMesh;
        }
    }
}
