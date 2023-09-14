using System.Collections;
using UnityEngine;

public class ElevatorController : MonoBehaviour
{
    public Transform leftDoor; // Левая дверь
    public Transform rightDoor; // Правая дверь
    
    private Vector3 leftDoorClosedPosition;
	private Vector3 rightDoorClosedPosition;
    private bool isDoorOpen = false;

    public float speed = 3.0f; // скорость лифта
    public float doorSpeed = 1.0f; // Скорость движения дверей
    public float doorWidth = 0.3f; // Расстояние, на которое двери должны двигаться
    public float waitTime = 2.0f; // время ожидания на этаже

    private Vector3 targetPosition;
 
    public Floor[] Floors { get; set; }
    void Start()
	{
		leftDoorClosedPosition = leftDoor.position;
		rightDoorClosedPosition = rightDoor.position;
	}
    
    public void PerformAction(int action)
    {
        switch (action)
        {
            case -1:
                break;
            case 0:
                MoveUp();
                break;
            case 1:
                MoveDown();
                break;
            case 2:
                CloseDoor();
                break;
            case 3:
                OpenDoor();
                break;
            case 4:
                break;
        }
    }


    public void CallElevator(int floorNumber)
    {
        if (floorNumber >= 0 && floorNumber < Floors.Length)
        {
            targetPosition = new Vector3(transform.position.x, Floors[floorNumber].transform.position.y - 0.5f, transform.position.z);
            StartCoroutine(MoveToTargetFloor());
        }
    }

    public void MoveUp()
    {
        if (transform.position.y < Floors[Floors.Length - 1].transform.position.y)
        {
            CallElevator(GetCurrentFloorNumber() + 1);
        }
    }

    public void MoveDown()
    {
        if (transform.position.y > Floors[0].transform.position.y)
        {
            CallElevator(GetCurrentFloorNumber() - 1);
        }
    }

    public void OpenDoor()
    {
        isDoorOpen = true;
        StartCoroutine(OpenDoors());
    }

    public void CloseDoor()
    {
        isDoorOpen = false;
        StartCoroutine(CloseDoors());
    }

    private int GetCurrentFloorNumber()
    {
        float closestDistance = float.MaxValue;
        int closestFloorNumber = 0;

        for (int i = 0; i < Floors.Length; i++)
        {
            float distance = Mathf.Abs(transform.position.y - Floors[i].transform.position.y);
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestFloorNumber = i;
            }
        }

        return closestFloorNumber;
    }

    private IEnumerator MoveToTargetFloor()
    {
        while (Vector3.Distance(transform.position, targetPosition) > 0.0005f)
        {
            transform.position = Vector3.MoveTowards(transform.position, targetPosition, speed * Time.deltaTime);
            yield return null;
        }

        if (isDoorOpen)
        {
            leftDoorClosedPosition = leftDoor.position + new Vector3(0, 0, doorWidth);
            rightDoorClosedPosition = rightDoor.position + new Vector3(0, 0, -doorWidth);
        }
        else
        {
            leftDoorClosedPosition = leftDoor.position;
            rightDoorClosedPosition = rightDoor.position; 
        }

        yield return new WaitForSeconds(waitTime);
    }

	private IEnumerator OpenDoors()
	{
		Vector3 leftDoorOpenPosition = leftDoorClosedPosition + new Vector3(0, 0, -doorWidth);
		Vector3 rightDoorOpenPosition = rightDoorClosedPosition + new Vector3(0, 0, doorWidth);

		while (Vector3.Distance(leftDoor.position, leftDoorOpenPosition) > 0.0005f)
		{
		    leftDoor.position = Vector3.MoveTowards(leftDoor.position, leftDoorOpenPosition, doorSpeed * Time.deltaTime);
		    rightDoor.position = Vector3.MoveTowards(rightDoor.position, rightDoorOpenPosition, doorSpeed * Time.deltaTime);
		    yield return null;
		}
	}

	private IEnumerator CloseDoors()
	{
		while (Vector3.Distance(leftDoor.position, leftDoorClosedPosition) > 0.0005f)
		{
		    leftDoor.position = Vector3.MoveTowards(leftDoor.position, leftDoorClosedPosition, doorSpeed * Time.deltaTime);
		    rightDoor.position = Vector3.MoveTowards(rightDoor.position, rightDoorClosedPosition, doorSpeed * Time.deltaTime);
		    yield return null;
		}
	}

}

